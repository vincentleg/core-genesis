/** Optional public map assets only; no arbitrary destinations or query payloads. */
function allowedMapAsset(raw){const u=new URL(raw);if(u.protocol!=='https:'||u.username||u.password||u.search||u.port)return false;
 if(u.hostname==='tiles.openfreemap.org')return u.pathname==='/planet'||/^\/(planet\/|fonts\/)/.test(u.pathname);
 if(u.hostname==='gibs.earthdata.nasa.gov')return /^\/wmts\/epsg3857\/best\/BlueMarble_ShadedRelief_Bathymetry\/default\/GoogleMapsCompatible_Level8\/\d+\/\d+\/\d+\.jpeg$/.test(u.pathname);
 return u.hostname==='s3.amazonaws.com'&&/^\/elevation-tiles-prod\/terrarium\/\d+\/\d+\/\d+\.png$/.test(u.pathname);
}
function publicHeaders(request){return Object.fromEntries(Object.entries(request.headers()).filter(([k])=>!['referer','cookie','authorization'].includes(k.toLowerCase())));}
module.exports={allowedMapAsset,publicHeaders};
