import React from 'react';

const IconCircle = ({ Icon, color, sz = 28 }) => (
  <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
    <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
  </div>
);

export default IconCircle;
