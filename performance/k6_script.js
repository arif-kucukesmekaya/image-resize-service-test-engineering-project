// Bu dosya: k6 yük ve performans testi senaryosu
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';
import encoding from 'k6/encoding';

// Tiny 1x1 pixel JPEG encoded in base64
const tinyJpegB64 = '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=';
const tinyJpegBin = encoding.b64decode(tinyJpegB64);

export const options = {
  vus: 50,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // p95 latency must be under 2s
    http_req_failed: ['rate<0.05'],     // error rate must be under 5%
  },
};

const resizeDuration = new Trend('resize_duration');
const resizeErrors = new Counter('resize_errors');

export default function () {
  const baseUrl = __ENV.API_BASE_URL || 'http://localhost:8000';
  
  const payload = {
    file: http.file(tinyJpegBin, 'sample.jpg', 'image/jpeg'),
    width: '300',
    height: '300',
    quality: '85',
    format: 'JPEG',
  };

  const response = http.post(`${baseUrl}/resize`, payload);

  const success = check(response, {
    'status is 200': (r) => r.status === 200,
    'has valid id': (r) => {
      try {
        const json = JSON.parse(r.body);
        return json.id !== undefined;
      } catch (e) {
        return false;
      }
    }
  });

  if (success) {
    resizeDuration.add(response.timings.duration);
  } else {
    resizeErrors.add(1);
  }

  sleep(1);
}

export function handleSummary(data) {
  return {
    'performance/results.json': JSON.stringify(data),
  };
}
