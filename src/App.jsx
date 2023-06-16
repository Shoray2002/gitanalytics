import { useEffect, useState } from "react";
import RepoFetch from "./comps/repofetch";
import Card from "./comps/card";

function App() {
  const [search, setSearch] = useState("");
  const [repoToFetch, setRepoToFetch] = useState("");
  const [data, setData] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (search === "") return;
    setRepoToFetch(search);
  };
  useEffect(() => {
    console.log(data);
  }, [data]);
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
          <RepoFetch userInput={repoToFetch} setData={setData} />
        </header>
        <div className="results">
          {data.map((datum, i) => {
            return <Card key={i} repo={datum} />;
          })}
        </div>
      </div>
    </main>
  );
}

export default App;
