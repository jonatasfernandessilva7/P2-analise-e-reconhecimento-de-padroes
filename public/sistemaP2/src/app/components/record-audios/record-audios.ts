import {ChangeDetectorRef, Component} from '@angular/core';
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

  isRecording:boolean = false;
  ml_prediction!: string;

  constructor(private apiService: ApiServiceRecord, private cdr: ChangeDetectorRef) {}

  startRecording() {
    this.isRecording = true;
    this.apiService.postIniciarAudio().subscribe({
      next: () => {
        console.log('Gravação iniciada');
      },
      error: (err) => console.error(err)
    });
  }

  stopRecording() {
    this.apiService.postPararAudio().subscribe({
      next: (response) => {
        console.log('Gravação parada', response);
        this.isRecording = false;
        this.ml_prediction = response?.body?.ml_prediction || 'Não reconhecido';
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error(err);
        this.isRecording = false;
        this.ml_prediction = 'Erro ao processar';
        this.cdr.detectChanges();
      }
    });
  }
}
