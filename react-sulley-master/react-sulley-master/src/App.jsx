// import { StrictMode } from 'react'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import Routes from './routes/index.jsx'
import AuthHydrator from './hooks/AuthHydrator.jsx'


function App() {

  return (
    <BrowserRouter> 
      <AuthHydrator>
        <Routes></Routes>
      </AuthHydrator>
    </BrowserRouter>
  )
}

export default App
