/* eslint-disable react/prop-types */
const Card = ({ repo, golden = false }) => {
  return (
    <div className={`result ${golden ? "golden" : "normal"}`}>
      <h3>{repo.repository_name}</h3>
      <a href={repo.repository_url} target="_black" rel="noreferrer">
        Complexity Score: {repo.complexity}
      </a>
    </div>
  );
};

export default Card;
