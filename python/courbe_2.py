# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 09:16:43 2024

@author: Romain
"""

import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok, adc2mV
import matplotlib.pyplot as plt
import wave
import os

# Paramètres globaux
sizeOfOneBuffer = 500  # Taille d'un seul buffer en nombre d'échantillons

def get_desktop_path():
    """Retourne le chemin du bureau de l'utilisateur."""
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    else:
        return os.path.join(os.path.expanduser('~'), 'Desktop')

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

def start_streaming_plot():
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
        totalSamples = 10000  # Nombre total de samples à capturer
        autoStopOn = 0
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

        print("Acquisition en cours...")

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
            plt.ion()  # Activer le mode interactif de matplotlib pour un affichage en temps réel

            # Créer la figure et l'axe pour le tracé en temps réel
            fig, ax = plt.subplots(figsize=(10, 6))
            line, = ax.plot([], [])
            ax.set_title('Données du Picoscope 2000 en temps réel')
            ax.set_xlabel('Échantillons')
            ax.set_ylabel('Amplitude (mV)')
            ax.grid(True)

            x_data = np.arange(totalSamples)
            y_data = np.zeros(totalSamples)

            line.set_data(x_data, y_data)
            ax.set_xlim(0, totalSamples)
            ax.set_ylim(-channel_range, channel_range)

            while not autoStopOuter:
                # Obtenir les dernières valeurs capturées
                status = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
                assert_pico_ok(status)

                # Mettre à jour les données affichées
                line.set_ydata(adc2mV(bufferCompleteA, channel_range, ctypes.c_int16(32767)))
                fig.canvas.draw()
                fig.canvas.flush_events()

        except KeyboardInterrupt:
            print("Arrêt manuel de l'acquisition.")

        finally:
            plt.ioff()  # Désactiver le mode interactif après l'acquisition
            plt.show()

            # Enregistrer les données dans un fichier WAV
            desktop_path = get_desktop_path()
            wav_filename = os.path.join(desktop_path, 'acquisition.wav')
            create_wav(bufferCompleteA, wav_filename)

    finally:
        # Arrêt de l'acquisition et fermeture du Picoscope
        ps.ps2000aStop(chandle)
        ps.ps2000aCloseUnit(chandle)

if __name__ == "__main__":
    start_streaming_plot()
