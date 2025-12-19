import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 3: Genre Distribution by Game Count (Horizontal Bar Chart)
 * Top 10 genres by number of games owned
 * Matches: model_development.ipynb
 */
const GenreCountBar = ({ data }) => {
  // Count games per genre
  const genreCounts = {};
  
  data?.forEach(game => {
    if (game.genres && Array.isArray(game.genres)) {
      game.genres.forEach(genre => {
        genreCounts[genre] = (genreCounts[genre] || 0) + 1;
      });
    }
  });

  // Convert to array and get top 10
  const topGenres = Object.entries(genreCounts)
    .map(([genre, count]) => ({ genre, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
    .reverse(); // Reverse for better visual flow

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: '#1e2329',
          padding: '12px',
          borderRadius: '8px',
          border: '2px solid #66c0f4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
        }}>
          <p style={{ color: '#fff', fontWeight: 'bold', margin: 0 }}>{payload[0].payload.genre}</p>
          <p style={{ color: '#10B981', margin: '4px 0 0 0' }}>{payload[0].value} games</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Genre Distribution by Game Count</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart 
          data={topGenres} 
          layout="vertical"
          margin={{ top: 20, right: 30, left: 120, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis type="number" stroke="#9CA3AF" />
          <YAxis 
            dataKey="genre" 
            type="category" 
            stroke="#9CA3AF"
            width={110}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" fill="#10B981" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

GenreCountBar.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    genres: PropTypes.arrayOf(PropTypes.string)
  }))
};

export default GenreCountBar;
