import { Suspense } from 'react';
import ForestNavigator from '../components/ForestNavigator';

export default function Page() {
  return (
    <Suspense fallback={<main className="loading-shell">Entering the Forest substrate…</main>}>
      <ForestNavigator />
    </Suspense>
  );
}
