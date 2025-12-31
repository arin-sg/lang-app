import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import IngestPage from './pages/IngestPage'
import LibraryPage from './pages/LibraryPage'
import ReviewPage from './pages/ReviewPage'
import DrillPage from './pages/DrillPage'
import CoachPage from './pages/CoachPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/ingest" replace />} />
          <Route path="ingest" element={<IngestPage />} />
          <Route path="library" element={<LibraryPage />} />
          <Route path="review" element={<ReviewPage />} />
          <Route path="drills" element={<DrillPage />} />
          <Route path="coach" element={<CoachPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
