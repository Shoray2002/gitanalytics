/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";
import "./repofetch.css";
const FetchPublicRepos = ({ userInput, setUserDataFetched }) => {
  const [publicRepos, setPublicRepos] = useState(0);
  useEffect(() => {
    const fetchRepos = async () => {
      const baseUrl = "https://api.github.com/users/";
      let userUrl;

      if (userInput.startsWith("https://github.com/")) {
        const username = userInput.split("https://github.com/")[1];
        userUrl = `${baseUrl}${username}`;
      } else if (userInput.startsWith("http://github.com/")) {
        const username = userInput.split("http://github.com/")[1];
        userUrl = `${baseUrl}${username}`;
      } else {
        userUrl = `${baseUrl}${userInput}`;
      }

      try {
        const response = await fetch(userUrl);
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const data = await response.json();
        setUserDataFetched(true);
        setPublicRepos(data.public_repos);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    if (userInput) {
      fetchRepos();
    }
  }, [setUserDataFetched, userInput]);

  return (
    publicRepos > 0 && (
      <div className="wrapper">
        <h3>Number of Public Repositories:</h3>
        <p>{publicRepos}</p>
      </div>
    )
  );
};

export default FetchPublicRepos;
