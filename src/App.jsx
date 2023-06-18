/* eslint-disable no-constant-condition */
import { useEffect, useState } from "react";
import RepoFetch from "./comps/repofetch";
import Card from "./comps/card";
import Loader from "./comps/Loader";

function App() {
  const [search, setSearch] = useState("");
  const [repoToFetch, setRepoToFetch] = useState("");
  const [userName, setUserName] = useState("");
  const [data, setData] = useState([]);
  const [goldenRepo, setGoldenRepo] = useState({});
  const [userDataFetched, setUserDataFetched] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  useEffect(() => {
    if (data.length) {
      const last = data.length - 1;
      setGoldenRepo({
        repository_name: data[last].most_complex_repository_name,
        repository_url: data[last].most_complex_repository_url,
        complexity: data[last].max_complexity,
      });
    }
  }, [data]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (search === "") return;
    setUserDataFetched(0);
    setRepoToFetch(search);
  };

  const handleAnalyze = async (userName) => {
    setAnalyzing(true);
    const decoder = new TextDecoder();
    const response = await fetch(
      `http://localhost:5000/analyze?username=${userName}`
    );
    const reader = response.body.getReader();
    const processChunks = async () => {
      while (true) {
        const { value: chunk, done: readerDone } = await reader.read();
        if (readerDone) {
          break;
        }
        const chunkString = decoder.decode(chunk);
        try {
          const parsedChunk = JSON.parse(chunkString);
          setData((prev) => {
            return [...prev, parsedChunk];
          });
        } catch (err) {
          console.log(err);
        }
      }
    };
    await processChunks();
    setAnalyzing(false);
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
            setUserName={setUserName}
          />
          {userDataFetched ? (
            <div
              className="analyzeButton"
              onClick={() => handleAnalyze(userName)}
            >
              Analyze Repos?
            </div>
          ) : (
            <div className="analyzeButton disabled" onClick={handleSearch}>
              Fetch User Data
            </div>
          )}
        </header>
        {data.length ? (
          <div className="results">
            <h3 className="headerline">Most Complex Repo</h3>
            <Card repo={goldenRepo} golden={true} />
            <h3 className="headerline">Analyzed Repositories</h3>
            {data.map((datum, i) => {
              return <Card key={i} repo={datum} />;
            })}
          </div>
        ) : null}
        {data.length < userDataFetched && analyzing && <Loader />}
      </div>
    </main>
  );
}

export default App;
