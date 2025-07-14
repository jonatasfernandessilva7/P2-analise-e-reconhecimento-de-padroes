import { TestBed } from '@angular/core/testing';

import { RecordAudio } from './record-audio';

describe('RecordAudio', () => {
  let service: RecordAudio;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RecordAudio);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
