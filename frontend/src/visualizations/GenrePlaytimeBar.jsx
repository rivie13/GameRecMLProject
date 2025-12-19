import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 4: Genre Distribution by Playtime (Horizontal Bar Chart)
 * Top 10 genres by hours played (more meaningful than count!)
 * Matches: model_development.ipynb
 */
const GenrePlaytimeBar = ({ data }) => {
  // Sum playtime per genre
  const genrePlaytime = {};
  
  data?.forEach(game => {
    if (game.genres && Array.isArray(game.genres) && game.playtime_hours) {
      game.genres.forEach(genre => {
        genrePlaytime[genre] = (genrePlaytime[genre] || 0) + game.playtime_hours;
      });
    }
  });

  // Convert to array and get top 10
  const topGenres = Object.entries(genrePlaytime)
    .map(([genre, hours]) => ({ 
      genre, 
      hours: Math.round(hours * 10) / 10 
    }))
    .sort((a, b) => b.hours - a.hours)
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
          <p style={{ color: '#F59E0B', margin: '4px 0 0 0' }}>{payload[0].value} hours</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Genre Distribution by Playtime</h3>
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
          <Bar dataKey="hours" fill="#F59E0B" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

GenrePlaytimeBar.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    genres: PropTypes.arrayOf(PropTypes.string),
    playtime_hours: PropTypes.number
  }))
};

export default GenrePlaytimeBar;
