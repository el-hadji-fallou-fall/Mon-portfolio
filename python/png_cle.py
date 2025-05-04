# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 15:09:56 2024

@author: Romain
"""

import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok, adc2mV
import wave
import os
import time
import matplotlib.pyplot as plt
import pyudev
from tkinter import Tk, Scale, Button, Frame, Label
import tkinter as tk

# Paramètres globaux
sizeOfOneBuffer = 1000  # Taille d'un seul buffer en nombre d'échantillons

def get_desktop_path():
    """Retourne le chemin du bureau de l'utilisateur."""
    return '/home/pi/Desktop/PFE/2024'  # Chemin pour le bureau spécifique

def list_usb_storage_devices(base_path='/media/pi'):
    context = pyudev.Context()
    devices = context.list_devices(subsystem='block', DEVTYPE='partition')

    mounted_devices = []

    for device in devices:
        if 'ID_BUS' in device and device['ID_BUS'] == 'usb':
            # Récupérer le nom personnalisé si possible
            device_name = device.get('ID_MODEL', 'Unknown_Model')
            vendor_name = device.get('ID_VENDOR', 'Unknown_Vendor')

            # Rechercher les montages dans le répertoire base_path
            mount_points = [os.path.join(base_path, d) for d in os.listdir(base_path)]
            for mount_point in mount_points:
                if os.path.ismount(mount_point):
                    mounted_devices.append((mount_point, f"{vendor_name}_{device_name}"))
                    print(f"Dispositif de stockage USB détecté: {mount_point} ({vendor_name} - {device_name})")

    if not mounted_devices:
        print("Aucun périphérique de stockage USB monté trouvé.")
    
    return mounted_devices

def create_wav(data, filename, frate=1250000.0):
    """Crée un fichier WAV à partir des données."""
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    nchannels = 1
    sampwidth = 2

    with wave.open(filename, 'w') as wav_file:
        wav_file.setparams((nchannels, sampwidth, int(frate), nframes, comptype, compname))
        wav_file.writeframes(data.tobytes())
    print(f"Fichier WAV créé: {filename}")

def create_png_plot(data, filename, channel_range):
    """Crée un fichier PNG du tracé de la courbe."""
    plt.figure(figsize=(10, 6))
    plt.plot(adc2mV(data, channel_range, ctypes.c_int16(32767)))
    plt.title("Acquisition")
    plt.xlabel("Échantillons")
    plt.ylabel("Amplitude (mV)")
    plt.grid()
    plt.savefig(filename)
    plt.close()
    print(f"Fichier PNG créé: {filename}")

def start_streaming_plot(duration):
    # Connexion au Picoscope 2000
    chandle = ctypes.c_int16()
    status = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
    assert_pico_ok(status)

    try:
        # Configuration du canal A
        channel_range = ps.PS2000A_RANGE['PS2000A_50MV']
        status = ps.ps2000aSetChannel(chandle,
                                      ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                                      1,  # enabled
                                      ps.PS2000A_COUPLING['PS2000A_AC'],
                                      channel_range,
                                      0.0)  # analogue offset
        assert_pico_ok(status)

        # Création du buffer pour recevoir les données du canal A
        bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
        memory_segment = 0

        # Définition du buffer de données pour le canal A
        status = ps.ps2000aSetDataBuffers(chandle,
                                          ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
                                          bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                          None,
                                          sizeOfOneBuffer,
                                          memory_segment,
                                          ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])
        assert_pico_ok(status)

        # Paramètres d'acquisition en mode streaming
        sampleInterval = ctypes.c_int32(80000)  # Interval d'échantillonnage en picosecondes (80ns)
        sampleUnits = ps.PS2000A_TIME_UNITS['PS2000A_PS']  # Unité de l'interval d'échantillonnage
        maxPreTriggerSamples = 0
        frate = 1250000.0  # Fréquence d'échantillonnage
        totalSamples = int(duration * frate)  # Nombre total de samples à capturer
        autoStopOn = 1  # Activer l'arrêt automatique de l'acquisition
        downsampleRatio = 1

        # Démarrage de l'acquisition en streaming
        status = ps.ps2000aRunStreaming(chandle,
                                        ctypes.byref(sampleInterval),
                                        sampleUnits,
                                        maxPreTriggerSamples,
                                        totalSamples,
                                        autoStopOn,
                                        downsampleRatio,
                                        ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'],
                                        sizeOfOneBuffer)
        assert_pico_ok(status)

        print(f"Acquisition en cours pour {duration} secondes...")

        # Buffer pour stocker les données complètes capturées
        bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
        nextSample = 0
        autoStopOuter = False

        def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
            nonlocal nextSample, autoStopOuter
            destEnd = nextSample + noOfSamples
            sourceEnd = startIndex + noOfSamples
            bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
            nextSample += noOfSamples
            if nextSample >= totalSamples:
                autoStopOuter = True

        # Convertir la fonction Python en pointeur de fonction C
        cFuncPtr = ps.StreamingReadyType(streaming_callback)

        try:
            # Attendre la fin de l'acquisition
            start_time = time.time()
            while time.time() - start_time < duration:
                status = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
                assert_pico_ok(status)
                time.sleep(0.1)

            # À la fin de l'acquisition, créer le fichier WAV et PNG
            usb_devices = list_usb_storage_devices()
            if usb_devices:
                usb_mount_point, usb_name = usb_devices[0]
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                wav_filename = os.path.join(usb_mount_point, f'acquisition_{usb_name}_{timestamp}.wav')
                create_wav(bufferCompleteA, wav_filename)
                png_filename = os.path.join(usb_mount_point, f'acquisition_{usb_name}_{timestamp}.png')
                create_png_plot(bufferCompleteA, png_filename, channel_range)
            else:
                print("Aucun périphérique de stockage USB monté trouvé. Impossible de sauvegarder les fichiers WAV et PNG.")

        except KeyboardInterrupt:
            print("Arrêt manuel de l'acquisition.")

    finally:
        # Arrêt de l'acquisition et fermeture du Picoscope
        ps.ps2000aStop(chandle)
        ps.ps2000aCloseUnit(chandle)

def update_duration(value):
    global duration
    duration = int(value)
    duration_label.config(text=f"Durée d'acquisition : {duration} secondes")

if __name__ == "__main__":
    duration = 30  # Durée par défaut de l'acquisition en secondes

    root = Tk()
    root.title("Acquisition Hydrophone")
    root.minsize(400, 240)
    root.config(background='#F7F9F9')

    frame = Frame(root, bg='#F7F9F9')
    frame.pack(expand=tk.YES, fill=tk.BOTH)

    duration_label = Label(frame, text=f"Durée d'acquisition : {duration} secondes", bg='#F7F9F9', fg='black', font=("Courrier", 10))
    duration_label.pack(pady=5)

    echelle = Scale(frame, from_=1, to=120, orient=tk.HORIZONTAL, command=update_duration,
                    resolution=1, tickinterval=10, length=300, label='Temps d\'acquisition (s)', bg='Black', fg='#F7F9F9')
    echelle.pack(pady=5, fill=tk.X)

    acquisition_button = Button(frame, text="Démarrer l'acquisition", font=("Courrier", 10), bg='Black', fg='#F7F9F9', command=lambda: start_streaming_plot(duration))
    acquisition_button.pack(pady=20, fill=tk.X)

    root.mainloop()
