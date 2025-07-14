import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecordAudios } from './record-audios';

describe('RecordAudios', () => {
  let component: RecordAudios;
  let fixture: ComponentFixture<RecordAudios>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecordAudios]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RecordAudios);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
