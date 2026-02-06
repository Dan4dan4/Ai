import RagChat from "./components/rag/RagChat";
import QueryBox from "./components/QueryBox";
import "./App.css";
import Navbar from "./components/layout/Navbar";
import UploadBox from "./components/upload/Upload";

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <h1>RAG</h1>
      <div className="fullscreen-box">
        <QueryBox />
        <UploadBox />
      </div>
    </div>
  );
}

export default App;
