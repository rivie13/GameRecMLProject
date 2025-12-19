import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 5: Engagement Score vs Playtime (Scatter Plot)
 * X-axis: Playtime (hours), Y-axis: Engagement score (0-100)
 * Point size = engagement level
 * Matches: feature_engineering.ipynb
 */
const EngagementScatter = ({ data }) => {
  // Filter and prepare data for scatter plot
  const scatterData = data
    ?.filter(game => game.engagement_score != null && game.playtime_hours > 0)
    .map(game => ({
      name: game.name || `Game ${game.appid}`,
      appid: game.appid,
      playtime: Math.round(game.playtime_hours * 10) / 10,
      engagement: Math.round(game.engagement_score),
      // Size based on engagement category
      size: game.playtime_hours > 50 ? 100 : game.playtime_hours > 5 ? 60 : 30
    })) || [];

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
          <p style={{ color: '#66c0f4', margin: '2px 0', fontSize: '14px' }}>Playtime: {data.playtime} hrs</p>
          <p style={{ color: '#10B981', margin: '2px 0', fontSize: '14px' }}>Engagement: {data.engagement}/100</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="chart-container">
      <h3 className="chart-title">Engagement Score vs Playtime</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            type="number" 
            dataKey="playtime" 
            name="Playtime (hrs)" 
            stroke="#9CA3AF"
            label={{ value: 'Playtime (hours)', position: 'insideBottom', offset: -10, fill: '#9CA3AF' }}
          />
          <YAxis 
            type="number" 
            dataKey="engagement" 
            name="Engagement" 
            stroke="#9CA3AF"
            label={{ value: 'Engagement Score', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
          />
          <ZAxis type="number" dataKey="size" range={[30, 100]} />
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
          <Scatter 
            data={scatterData} 
            fill="#66c0f4" 
            fillOpacity={0.6}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

EngagementScatter.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string,
    playtime_hours: PropTypes.number,
    engagement_score: PropTypes.number
  }))
};

export default EngagementScatter;
