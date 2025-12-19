import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import PropTypes from 'prop-types';

/**
 * Chart 6: Feature Importance (Horizontal Bar Chart)
 * Shows top 15 ML features by importance
 * Great for "how it works" explanation!
 * Matches: feature_engineering.ipynb
 */
const FeatureImportanceBar = ({ featureImportanceData }) => {
  // featureImportanceData should come from API (top 15 features)
  // Format: [{ feature: 'tag_Open-World', importance: 0.15 }, ...]
  
  const topFeatures = featureImportanceData
    ?.slice(0, 15)
    .map(item => ({
      feature: item.feature.replace('tag_', '').replace('_', ' '),
      importance: Math.round(item.importance * 1000) / 10 // Convert to percentage
    }))
    .reverse() || []; // Reverse for better visual flow

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
          <p style={{ color: '#fff', fontWeight: 'bold', margin: 0 }}>{payload[0].payload.feature}</p>
          <p style={{ color: '#A855F7', margin: '4px 0 0 0' }}>Importance: {payload[0].value}%</p>
        </div>
      );
    }
    return null;
  };

  if (!featureImportanceData || featureImportanceData.length === 0) {
    return (
      <div className="chart-container">
        <h3 className="chart-title">Feature Importance</h3>
        <p className="text-gray-400 text-center py-10">No feature importance data available</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3 className="chart-title">ML Feature Importance (Top 15)</h3>
      <ResponsiveContainer width="100%" height={500}>
        <BarChart 
          data={topFeatures} 
          layout="vertical"
          margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis type="number" stroke="#9CA3AF" unit="%" />
          <YAxis 
            dataKey="feature" 
            type="category" 
            stroke="#9CA3AF"
            width={140}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" fill="#A855F7" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

FeatureImportanceBar.propTypes = {
  featureImportanceData: PropTypes.arrayOf(PropTypes.shape({
    feature: PropTypes.string.isRequired,
    importance: PropTypes.number.isRequired
  }))
};

export default FeatureImportanceBar;
