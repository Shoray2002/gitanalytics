/* eslint-disable react/prop-types */
const Card = ({ repo }) => {
  return (
    <div className="result">
      <h3>{repo.name}</h3>
      <a href={repo.html_url} target="_black" rel="noreferrer">
        Visit
      </a>
    </div>
  );
};

export default Card;
