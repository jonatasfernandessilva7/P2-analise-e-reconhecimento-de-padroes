import soundfile as sf
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import os

def analisar_som_fourier(file:str):

    try:

        data, samplerate = sf.read(file) 

        '''This excerpt convert audio for mono'''
        if len(data.shape) > 1: 
            data = data[:, 0]

        N = len(data) 
        yf = fft(data) 
        xf = fftfreq(N, 1 / samplerate)

        '''This excerpt filter frequencies positives and your correspondents amplitudes'''
        idx = np.where(xf > 0) 
        frequencias = xf[idx]
        amplitudes = np.abs(yf[idx])

        '''This excerpt displays exists characteristics'''
        pico_frequencia = frequencias[np.argmax(amplitudes)] 
        pico_amplitude = np.max(amplitudes)
        energia_total = np.sum(data ** 2)
        media_abs = np.mean(np.abs(data))

        '''
            This excerpt calculate a spectral centroid,
            this centroid is represented for weighted average   
            of frequencies by amplitudes.
        '''
        if np.sum(amplitudes) > 0:
            centroide_espectral = np.sum(frequencias * amplitudes) / np.sum(amplitudes)
        else:
            centroide_espectral = 0.0

        '''
            Spectral Bandwidth (a measure of frequency dispersion).
            Calculates the standard deviation of frequencies weighted by amplitudes
        '''
        if np.sum(amplitudes) > 0:
            largura_banda_espectral = np.sqrt(np.sum(amplitudes * (frequencias - centroide_espectral)**2) / np.sum(amplitudes))
        else:
            largura_banda_espectral = 0.0

        '''
            Zero Crossing Rate
        '''
        zcr = np.sum(np.abs(np.diff(np.sign(data)))) / (2 * N)

        return {
            "pico_frequencia": float(pico_frequencia),
            "pico_amplitude": float(pico_amplitude),
            "energia_total": float(energia_total),
            "media_abs": float(media_abs),
            "centroide_espectral": float(centroide_espectral),
            "largura_banda_espectral": float(largura_banda_espectral),
            "zcr": float(zcr),
            "status": "analisado"
        }
    
    except Exception as e:

        return {"erro": str(e)}

def filtro_passa_baixa(signal, rate, cutoff=4000):

    nyquist = 0.5 * rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(6, normal_cutoff, btype='low', analog=False)

    return lfilter(b, a, signal)

def detectar_padroes(signal, rate):

    energia = np.sum(signal ** 2)

    if energia > 1e12:
        return "Explosão detectada"
    
    elif np.mean(np.abs(signal)) > 1000:
        return "Grito ou alarme detectado"   
    
    elif energia == 0:
        return "Ambiente calmo ou desconhecido"

    else:
        return "situação não identificada"

def salvar_espectrograma(signal, rate, timestamp):

    pasta = "../relatorios/espectogramas"
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"espectrograma_{timestamp}.png")

    plt.figure(figsize=(10, 4))
    plt.specgram(signal, Fs=rate, NFFT=1024, noverlap=512, cmap='inferno')
    plt.title("Espectrograma de Áudio")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Frequência (Hz)")
    plt.colorbar(label='Intensidade')
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho




