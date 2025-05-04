import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok, adc2mV
import matplotlib.pyplot as plt
import wave
import os
import time

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

            # À la fin de l'acquisition, créer le fichier WAV
            wav_filename = os.path.join(get_desktop_path(), f'acquisition_{time.strftime("%Y%m%d-%H%M%S")}.wav')
            create_wav(bufferCompleteA, wav_filename)

            # Créer le fichier PNG du tracé de la courbe
            png_filename = os.path.join(get_desktop_path(), f'acquisition_{time.strftime("%Y%m%d-%H%M%S")}.png')
            create_png_plot(bufferCompleteA, png_filename, channel_range)

        except KeyboardInterrupt:
            print("Arrêt manuel de l'acquisition.")

    finally:
        # Arrêt de l'acquisition et fermeture du Picoscope
        ps.ps2000aStop(chandle)
        ps.ps2000aCloseUnit(chandle)

if __name__ == "__main__":
    duration = 20.0  # Durée de l'acquisition en secondes
    start_streaming_plot(duration)
