// Fixture (story #189): a web screen that breaks every web vibe rule at least once. The scorer must fail it.
// Read as text only; this file is never compiled.
import { Button } from '@mui/material';

export function BadScreen() {
  return (
    <div style={{ background: '#112233', padding: '16px', color: 'rgb(255, 0, 0)' }}>
      <button onClick={() => {}}>Sign in</button>
      <input type="email" />
      <canvas width={300} height={100} />
      <Button>Fancy</Button>
    </div>
  );
}
