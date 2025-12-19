import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 2: Top 10 Most Played Games (Horizontal Bar Chart)
 * Game names on Y-axis, hours played on X-axis
 * Matches: model_development.ipynb
 */
const TopGamesBar = ({ data }) => {
  // Get top 10 games by playtime
  const topGames = data
    ?.filter(game => game.playtime_hours > 0)
    .sort((a, b) => b.playtime_hours - a.playtime_hours)
    .slice(0, 10)
    .map(game => ({
      name: game.name.length > 30 ? game.name.substring(0, 30) + '...' : game.name,
      hours: Math.round(game.playtime_hours * 10) / 10
    }))
    .reverse() || []; // Reverse for better visual flow (highest at top)

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: '#1e2329',
          padding: '12px',
          borderRadius: '8px',
          border: '2px solid #66c0f4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          maxWidth: '300px'
        }}>
          <p style={{ color: '#fff', fontWeight: 'bold', margin: 0 }}>{payload[0].payload.name}</p>
          <p style={{ color: '#66c0f4', margin: '4px 0 0 0' }}>{payload[0].value} hours</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Top 10 Most Played Games</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart 
          data={topGames} 
          layout="vertical"
          margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis type="number" stroke="#9CA3AF" />
          <YAxis 
            dataKey="name" 
            type="category" 
            stroke="#9CA3AF"
            width={140}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="hours" fill="#66c0f4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

TopGamesBar.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    playtime_hours: PropTypes.number.isRequired
  }))
};

export default TopGamesBar;
