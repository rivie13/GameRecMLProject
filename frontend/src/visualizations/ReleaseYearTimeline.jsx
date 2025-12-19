import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 7: Release Year Timeline (Scatter Plot)
 * X-axis: Release year (2000-2025), Y-axis: Playtime (hours)
 * Point size: Engagement score, Color: Genre or playtime category
 * Shows if you prefer new releases vs classics
 * NOTE: Only ~11% of games have release date data
 * Matches: Data from src/data_retrieval/get_release_dates.py
 */
const ReleaseYearTimeline = ({ data }) => {
  // Filter games with release_year and playtime > 0
  const timelineData = data
    ?.filter(game => 
      game.release_year != null && 
      game.playtime_hours > 0 &&
      game.release_year >= 2000 &&
      game.release_year <= 2025
    )
    .map(game => ({
      name: game.name,
      year: game.release_year,
      playtime: Math.round(game.playtime_hours * 10) / 10,
      engagement: game.engagement_score || 0,
      size: game.engagement_score ? game.engagement_score : 30,
      // Color based on playtime category
      category: game.playtime_hours > 50 ? 'Loved' : 
                game.playtime_hours > 5 ? 'Played' : 'Tried'
    })) || [];

  const getCategoryColor = (category) => {
    switch(category) {
      case 'Loved': return '#10B981'; // Green
      case 'Played': return '#3B82F6'; // Blue
      case 'Tried': return '#F59E0B'; // Orange
      default: return '#66c0f4'; // Cyan
    }
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: '#1e2329',
          padding: '12px',
          borderRadius: '8px',
          border: '2px solid #66c0f4',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          maxWidth: '300px'
        }}>
          <p style={{ color: '#fff', fontWeight: 'bold', margin: 0, marginBottom: '4px' }}>{data.name}</p>
          <p style={{ color: '#9CA3AF', margin: '2px 0', fontSize: '14px' }}>Year: {data.year}</p>
          <p style={{ color: '#66c0f4', margin: '2px 0', fontSize: '14px' }}>Playtime: {data.playtime} hrs</p>
          <p style={{ color: '#10B981', margin: '2px 0', fontSize: '14px' }}>Category: {data.category}</p>
        </div>
      );
    }
    return null;
  };

  if (timelineData.length === 0) {
    return (
      <div className="chart-container">
        <h3 className="chart-title">Release Year Timeline</h3>
        <p className="text-gray-400 text-center py-10">
          No release year data available (only ~11% of games have this data)
        </p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3 className="chart-title">Release Year Timeline</h3>
      <p className="text-gray-400 text-sm mb-2">
        Showing {timelineData.length} games with release date data
      </p>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            type="number" 
            dataKey="year" 
            domain={[2000, 2025]}
            name="Release Year" 
            stroke="#9CA3AF"
            label={{ value: 'Release Year', position: 'insideBottom', offset: -10, fill: '#9CA3AF' }}
          />
          <YAxis 
            type="number" 
            dataKey="playtime" 
            name="Playtime" 
            stroke="#9CA3AF"
            label={{ value: 'Playtime (hours)', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
          />
          <ZAxis type="number" dataKey="size" range={[30, 150]} />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
          <Scatter 
            data={timelineData.filter(d => d.category === 'Tried')} 
            fill={getCategoryColor('Tried')} 
            fillOpacity={0.6}
            name="Tried (0-5 hrs)"
          />
          <Scatter 
            data={timelineData.filter(d => d.category === 'Played')} 
            fill={getCategoryColor('Played')} 
            fillOpacity={0.6}
            name="Played (5-50 hrs)"
          />
          <Scatter 
            data={timelineData.filter(d => d.category === 'Loved')} 
            fill={getCategoryColor('Loved')} 
            fillOpacity={0.6}
            name="Loved (50+ hrs)"
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

ReleaseYearTimeline.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    release_year: PropTypes.number,
    playtime_hours: PropTypes.number,
    engagement_score: PropTypes.number
  }))
};

export default ReleaseYearTimeline;
