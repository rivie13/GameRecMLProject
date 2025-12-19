import { useMemo } from 'react';
import PropTypes from 'prop-types';

/**
 * Chart 8: Tag Cloud (Custom Implementation)
 * Size = playtime-weighted tag importance
 * Compatible with React 19 (no external library needed)
 */
const TagCloud = ({ data }) => {
  // Calculate tag importance based on playtime
  const tagData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const tagWeights = {};
    
    // Sum playtime-weighted tag votes
    data.forEach(game => {
      if (game.tags && Array.isArray(game.tags) && game.playtime_hours) {
        game.tags.forEach(tag => {
          // Weight by playtime (loved games contribute more)
          const weight = game.playtime_hours > 50 ? 3 : 
                        game.playtime_hours > 5 ? 2 : 1;
          tagWeights[tag] = (tagWeights[tag] || 0) + weight;
        });
      }
    });

    // Convert to array and get top 50 tags
    const tags = Object.entries(tagWeights)
      .map(([tag, weight]) => ({ tag, weight }))
      .sort((a, b) => b.weight - a.weight)
      .slice(0, 50);

    // Normalize weights for font sizes (12px to 48px)
    const maxWeight = Math.max(...tags.map(t => t.weight));
    const minWeight = Math.min(...tags.map(t => t.weight));
    const weightRange = maxWeight - minWeight || 1;

    return tags.map(({ tag, weight }) => ({
      tag,
      weight,
      // Font size between 12px and 48px
      fontSize: 12 + ((weight - minWeight) / weightRange) * 36,
      // Color intensity based on weight
      opacity: 0.5 + ((weight - minWeight) / weightRange) * 0.5
    }));
  }, [data]);

  // Generate random but consistent positions
  const getRandomPosition = (index) => {
    // Use index as seed for consistent positioning
    const angle = (index * 137.5) % 360; // Golden angle for nice distribution
    const radius = 30 + (index % 3) * 15; // Vary radius in rings
    
    return {
      left: `${50 + radius * Math.cos(angle * Math.PI / 180)}%`,
      top: `${50 + radius * Math.sin(angle * Math.PI / 180)}%`,
    };
  };

  if (tagData.length === 0) {
    return (
      <div className="chart-container">
        <h3 className="chart-title">Tag Cloud</h3>
        <p className="text-gray-400 text-center py-10">No tag data available</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3 className="chart-title">Your Gaming Tags</h3>
      <p className="text-gray-400 text-sm mb-4">
        Tag size represents playtime-weighted importance (top 50 tags)
      </p>
      <div 
        className="relative w-full bg-gray-900 rounded-lg p-8"
        style={{ minHeight: '400px' }}
      >
        {/* Grid layout for better spacing */}
        <div className="flex flex-wrap justify-center items-center gap-3">
          {tagData.map((item, index) => (
            <span
              key={item.tag}
              className="tag-cloud-item transition-all duration-200 hover:scale-110 cursor-pointer"
              style={{
                fontSize: `${item.fontSize}px`,
                color: '#66c0f4',
                opacity: item.opacity,
                fontWeight: item.fontSize > 30 ? 'bold' : 'normal',
                padding: '4px 8px',
              }}
              title={`${item.tag} (weight: ${item.weight})`}
            >
              {item.tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

TagCloud.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({
    tags: PropTypes.arrayOf(PropTypes.string),
    playtime_hours: PropTypes.number
  }))
};

export default TagCloud;
