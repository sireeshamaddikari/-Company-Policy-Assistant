import { Route, Routes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import { ChatProvider } from "./context/ChatContext";
import ChatPage from "./pages/ChatPage";
import DocumentsPage from "./pages/DocumentsPage";

/**
 * Root application component: chat session provider + app shell + routes.
 */
function App() {
  return (
    <ChatProvider>
      <AppLayout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
        </Routes>
      </AppLayout>
    </ChatProvider>
  );
}

export default App;
