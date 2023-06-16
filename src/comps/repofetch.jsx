/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";
import "./repofetch.css";
const FetchPublicRepos = ({ userInput, setData }) => {
  const [publicRepos, setPublicRepos] = useState(0);
  useEffect(() => {
    const fetchRepos = async () => {
      const baseUrl = "https://api.github.com/users/";
      let userUrl;

      if (userInput.startsWith("https://github.com/")) {
        const username = userInput.split("https://github.com/")[1];
        userUrl = `${baseUrl}${username}/repos?per_page=100`;
      } else if (userInput.startsWith("http://github.com/")) {
        const username = userInput.split("http://github.com/")[1];
        userUrl = `${baseUrl}${username}/repos?per_page=100`;
      } else {
        userUrl = `${baseUrl}${userInput}/repos?per_page=100`;
      }

      try {
        const response = await fetch(userUrl);
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const data = await response.json();
        setData(data);
        setPublicRepos(data.length);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
    if (userInput) {
      fetchRepos();
    }
  }, [setData, userInput]);

  return (
    <div className="wrapper">
      <h3>Number of Public Repositories:</h3>
      <p>{publicRepos}</p>
    </div>
  );
};

export default FetchPublicRepos;
