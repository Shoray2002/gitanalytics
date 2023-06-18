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
  const [userDataFetched, setUserDataFetched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (search === "") return;
    setRepoToFetch(search);
  };

  const handleAnalyze = async (userName) => {
    let result = "";
    const decoder = new TextDecoder();
    const response = await fetch(
      `http://localhost:5000/analyze?username=${userName}`
    );
    console.log(response);
    // the response body is a readable stream. the api will stream the data back to the client
    const reader = response.body.getReader();
    // read() returns a promise that resolves when a value has been received
    const { value: chunk, done: readerDone } = await reader.read();
    // if the stream is done, break the loop
    if (readerDone) return;
    // decode the received chunk
    const chunkString = decoder.decode(chunk);
    // append the decoded string to the result
    result += chunkString;
    // when we're done reading the stream, parse the result
    const parsedResult = JSON.parse(result);

    console.log(result);
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
