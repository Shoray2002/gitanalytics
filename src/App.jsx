import { useEffect, useState } from "react";
import RepoFetch from "./comps/repofetch";
import Card from "./comps/card";
import Loader from "./comps/Loader";

function App() {
  const [search, setSearch] = useState("");
  const [repoToFetch, setRepoToFetch] = useState("");
  // const [data, setData] = useState([]);
  const [userDataFetched, setUserDataFetched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (search === "") return;
    setRepoToFetch(search);
  };
  return (
    <main>
      <div className="App">
        <header>
          <h1>GitAnalytics</h1>
          <form className="search-box" onSubmit={handleSearch}>
            <input
              type="search"
              placeholder="Type here..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </form>
          <RepoFetch
            userInput={repoToFetch}
            setUserDataFetched={setUserDataFetched}
          />
          {userDataFetched ? (
            <div className="analyzeButton">Analyze Repos?</div>
          ) : (
            <div className="analyzeButton disabled" onClick={handleSearch}>
              Fetch User Data
            </div>
          )}
        </header>
        {/* {false ? (
          <>
            <div className="results">
              <h3>Public Repositories</h3>
            </div>
          </>
        ) : (
          <Loader />
        )} */}
      </div>
    </main>
  );
}

export default App;
