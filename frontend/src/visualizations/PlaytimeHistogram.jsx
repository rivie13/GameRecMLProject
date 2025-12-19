import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 1: Playtime Distribution Histogram
 * Shows engagement categories (tried/played/loved)
 * Matches: model_development.ipynb & hybrid_recommendations.ipynb
 */
const PlaytimeHistogram = ({ data }) => {
  // Transform data into histogram format
  const histogramData = [
    {
      category: 'Unplayed (0 hrs)',
      count: data?.filter(game => game.playtime_hours === 0).length || 0,
      fill: '#6B7280' // Gray
    },
    {
      category: 'Tried (0-5 hrs)',
      count: data?.filter(game => game.playtime_hours > 0 && game.playtime_hours <= 5).length || 0,
      fill: '#F59E0B' // Orange
    },
    {
      category: 'Played (5-50 hrs)',
      count: data?.filter(game => game.playtime_hours > 5 && game.playtime_hours <= 50).length || 0,
      fill: '#3B82F6' // Blue
    },
    {
      category: 'Loved (50+ hrs)',
      count: data?.filter(game => game.playtime_hours > 50).length || 0,
      fill: '#10B981' // Green
    }
  ];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: '#1e2329',
          padding: '12px',
          borderRadius: '8px',
          border: '2px solid #66c0f4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
        }}>
          <p style={{ color: '#fff', fontWeight: 'bold', margin: 0 }}>{data.category}</p>
          <p style={{ color: '#66c0f4', margin: '4px 0 0 0' }}>{data.count} games</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Playtime Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={histogramData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="category" 
            stroke="#9CA3AF"
            angle={-15}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#9CA3AF" />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" fill="#66c0f4" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

PlaytimeHistogram.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    playtime_hours: PropTypes.number
  }))
};

export default PlaytimeHistogram;
