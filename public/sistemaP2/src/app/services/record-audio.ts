import { Injectable } from '@angular/core';
import { HttpClient} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class ApiServiceRecord {

  private baseUrl: string = 'https://p2-analise-e-reconhecimento-de-padroes.onrender.com/v1';

  constructor(private http: HttpClient) { }

  postIniciarAudio() : Observable<any> {
    return this.http.post(`${this.baseUrl}/iniciar-gravacao`, {})
  }

  postPararAudio(): Observable<any> {
    return this.http.post(`${this.baseUrl}/parar-gravacao`, {})
  }

}
