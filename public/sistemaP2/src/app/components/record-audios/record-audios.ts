import { ChangeDetectorRef, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiServiceRecord } from '../../services/record-audio';

@Component({
  selector: 'app-record-audios',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './record-audios.html',
  styleUrl: './record-audios.css'
})
export class Record {

  isRecording: boolean = false;
  ml_prediction!: string;
  mediaRecorder!: MediaRecorder;
  chunks: Blob[] = [];

  constructor(
    private apiService: ApiServiceRecord,
    private cdr: ChangeDetectorRef
  ) {}

  startRecording() {
    this.ml_prediction = '';
    this.isRecording = true;
    this.chunks = [];

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      this.mediaRecorder = new MediaRecorder(stream, {mimeType: 'audio/webm'});
      this.mediaRecorder.start();

      this.mediaRecorder.ondataavailable = e => {
        this.chunks.push(e.data);
      };

      console.log('🎙️ Gravação iniciada');
    }).catch(err => {
      console.error('Erro ao acessar microfone:', err);
      this.isRecording = false;
    });
  }

  stopRecording() {
    if (!this.mediaRecorder) return;

    this.mediaRecorder.stop();

    this.mediaRecorder.onstop = () => {
      const audioBlob = new Blob(this.chunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('file', audioBlob, 'gravacao.webm');

      this.apiService.enviarAudio(formData).subscribe({
        next: (response) => {
          console.log('🔍 Processamento retornado:', response);
          this.ml_prediction = response.body?.ml_prediction || 'Não reconhecido';
          this.isRecording = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error('Erro ao processar áudio:', err);
          this.ml_prediction = 'Erro';
          this.isRecording = false;
          this.cdr.detectChanges();
        }
      });
    };
  }
}
