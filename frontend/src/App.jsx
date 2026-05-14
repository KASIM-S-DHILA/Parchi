import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import EffectiveStock from './pages/EffectiveStock';
import ChallanList from './pages/ChallanList';
import CreateChallan from './pages/CreateChallan';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<EffectiveStock />} />
          <Route path="challans" element={<ChallanList />} />
          <Route path="challans/new" element={<CreateChallan />} />
          <Route path="stock" element={<EffectiveStock />} />
          <Route path="ledgers" element={<div className="page"><h1>Parties</h1><p>Coming in Phase 2</p></div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
