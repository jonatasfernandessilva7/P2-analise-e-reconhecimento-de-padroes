import {Component, OnInit} from '@angular/core';
import { CommonModule } from '@angular/common';
import {ApiServiceRecord} from '../../services/record-audio';

@Component({
  selector: 'app-record-audios',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './record-audios.html',
  styleUrl: './record-audios.css'
})
export class Record {

  isRecording: boolean = false;
  statusMessage: string = 'Pronto pra gravar';
  responseMessage: any;

  constructor(private apiServiceAudio: ApiServiceRecord) { }

  startRecording() {
    alert('Gravação da reunião iniciada!');
    this.statusMessage = 'Iniciando Gravacao!';
    this.apiServiceAudio.postIniciarAudioReuniao().subscribe({
      next: (response) => {
        this.statusMessage = response.message;
        this.isRecording = true;
        this.responseMessage = response;
      },
      error: (error) => {
        this.statusMessage = `Erro ao iniciar gravacao: ${error.message}`;
        console.log(error);
      }
    });

  }

  stopRecording() {
    this.statusMessage = 'Parando gravação e processando áudio...';
    this.apiServiceAudio.postPararAudioReuniao().subscribe({
      next: (response) => {
        console.log("estou aqui");
        this.statusMessage = 'Gravação Encerrada e processada!';
        this.isRecording = false;
        this.responseMessage = response;
      },
      error: (error) => {
        this.statusMessage = `Erro ao parar gravação: ${error.error.detail || error.message}`;
        console.error(error);
      }
    });
  }
}
