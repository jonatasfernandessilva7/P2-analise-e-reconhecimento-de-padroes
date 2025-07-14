import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Record } from './components/record-audios/record-audios';

export const routes: Routes = [
    {
      path: "",
      component: Home
    },
    {
      path: "home",
      component: Home
    },
    {
      path: "gravar-audio",
      component: Record
    },
  ];
