const backend = process.env.HUMBERTITO_API_URL ?? 'http://127.0.0.1:8000';

export default {
  poweredByHeader: false,
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${backend}/api/:path*` }];
  },
};
