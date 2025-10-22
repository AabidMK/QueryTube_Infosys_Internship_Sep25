import React from 'react';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import MoreVertIcon from '@mui/icons-material/MoreVert';

const VideoCardClean = ({ video = {} }) => {
  const [thumbIdx, setThumbIdx] = React.useState(0);
  const qualities = ['maxresdefault', 'hqdefault', 'mqdefault', 'default'];

  const getThumbnail = () => {
    const id = video.video_id || video.videoId || video.id;
    if (!id) return 'https://via.placeholder.com/480x360.png?text=No+Thumbnail';
    return `https://img.youtube.com/vi/${id}/${qualities[thumbIdx]}.jpg`;
  };

  const handleThumbError = () => {
    if (thumbIdx < qualities.length - 1) setThumbIdx((s) => s + 1);
  };

  const openVideo = () => {
    const id = video.video_id || video.videoId || video.id;
    if (!id) return;
    window.open(`https://www.youtube.com/watch?v=${id}`, '_blank', 'noopener,noreferrer');
  };

  const formatViews = (v) => {
    if (!v) return '0 views';
    if (v >= 1000000) return `${(v / 1000000).toFixed(1)}M views`;
    if (v >= 1000) return `${(v / 1000).toFixed(1)}K views`;
    return `${v} views`;
  };

  return (
    <Card onClick={openVideo} sx={{ width: { xs: '100%', sm: 340 }, cursor: 'pointer' }} elevation={0}>
      <CardMedia component="img" image={getThumbnail()} alt={video.title || 'video'} onError={handleThumbError} sx={{ height: 190, objectFit: 'cover' }} />
      <CardContent sx={{ display: 'flex', gap: 1, p: 2, alignItems: 'flex-start' }}>
        <Box sx={{ mr: 1 }}>
          <Avatar sx={{ width: 36, height: 36 }} src={video.channelAvatar} alt={video.channel} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '1rem', lineHeight: 1.2, mb: 0.5, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
            {video.title}
          </Typography>
          <Typography variant="body2" sx={{ color: '#606060', fontSize: '0.9rem' }}>{video.channel}</Typography>
          <Typography variant="body2" sx={{ color: '#606060', fontSize: '0.9rem', mt: 0.3 }}>{formatViews(video.views)}</Typography>
        </Box>
        <IconButton size="small" onClick={(e) => e.stopPropagation()}>
          <MoreVertIcon />
        </IconButton>
      </CardContent>
    </Card>
  );
};

export default VideoCardClean;
