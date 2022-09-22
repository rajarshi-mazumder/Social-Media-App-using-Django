import {
  BrowserRouter as Router,
  Route,
  Routes, Link, useParams
} from "react-router-dom";
import './App.css';
import Header from './components/header'
import PostsListPage from './pages/PostsListsPage'
import PostPage from './pages/PostPage'

function App() {
  return (
    <Router>
      <div className="container dark">
        <div className="app">
          <Header />
          <Routes>
            <Route path="/" element={<PostsListPage />} exact />
            <Route path="/post/:id" element={<PostPage />} />
          </Routes>
          {/* <Routes>
          <Route path="/" exact component={PostsListPage} />
        </Routes> */}
        </div>
      </div>
    </Router>
  );
}

export default App;
