import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/APIDocumentation.css';

interface Endpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  description: string;
  tags: string[];
}

export const APIDocumentation: React.FC = () => {
  const navigate = useNavigate();
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [openApiSpec, setOpenApiSpec] = useState<any>(null);

  useEffect(() => {
    fetchAPISpec();
  }, []);

  const fetchAPISpec = async () => {
    try {
      const response = await fetch('/openapi.json');
      if (!response.ok) throw new Error('Failed to fetch API spec');
      const spec = await response.json();
      setOpenApiSpec(spec);

      const endpointList: Endpoint[] = [];
      Object.entries(spec.paths || {}).forEach(([path, methods]: [string, any]) => {
        Object.entries(methods).forEach(([method, details]: [string, any]) => {
          if (typeof details === 'object' && details.operationId) {
            endpointList.push({
              path,
              method: method.toUpperCase() as any,
              description: details.summary || details.description || 'No description',
              tags: details.tags || []
            });
          }
        });
      });

      setEndpoints(endpointList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load API documentation');
    } finally {
      setLoading(false);
    }
  };

  const allTags = Array.from(new Set(endpoints.flatMap(e => e.tags)));
  const filteredEndpoints = selectedTag
    ? endpoints.filter(e => e.tags.includes(selectedTag))
    : endpoints;

  const methodColor = (method: string) => {
    switch (method) {
      case 'GET': return '#3498db';
      case 'POST': return '#27ae60';
      case 'PUT': return '#f39c12';
      case 'DELETE': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="api-docs">
      <header className="docs-header">
        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
        <h1>📚 API Documentation</h1>
        <p>All available endpoints in CodePulse AI</p>
      </header>

      <main className="docs-content">
        {loading ? (
          <div className="loading">Loading API documentation...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : (
          <>
            <div className="docs-sidebar">
              <h3>Filter by Category</h3>
              <button
                className={`tag-btn ${!selectedTag ? 'active' : ''}`}
                onClick={() => setSelectedTag('')}
              >
                All ({endpoints.length})
              </button>
              {allTags.map(tag => (
                <button
                  key={tag}
                  className={`tag-btn ${selectedTag === tag ? 'active' : ''}`}
                  onClick={() => setSelectedTag(tag)}
                >
                  {tag} ({endpoints.filter(e => e.tags.includes(tag)).length})
                </button>
              ))}
            </div>

            <div className="docs-main">
              <div className="endpoints-list">
                {filteredEndpoints.length > 0 ? (
                  filteredEndpoints.map((endpoint, idx) => (
                    <div key={idx} className="endpoint-card">
                      <div className="endpoint-header">
                        <span
                          className="method-badge"
                          style={{ background: methodColor(endpoint.method) }}
                        >
                          {endpoint.method}
                        </span>
                        <code className="endpoint-path">{endpoint.path}</code>
                      </div>
                      <p className="endpoint-description">{endpoint.description}</p>
                      {endpoint.tags.length > 0 && (
                        <div className="endpoint-tags">
                          {endpoint.tags.map(tag => (
                            <span key={tag} className="endpoint-tag">{tag}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <p>No endpoints found for this category</p>
                  </div>
                )}
              </div>

              <div className="api-info">
                <h3>API Information</h3>
                {openApiSpec && (
                  <div className="info-card">
                    <p><strong>Title:</strong> {openApiSpec.info?.title}</p>
                    <p><strong>Version:</strong> {openApiSpec.info?.version}</p>
                    <p><strong>Description:</strong> {openApiSpec.info?.description}</p>
                    {openApiSpec.servers && (
                      <>
                        <p><strong>Base URLs:</strong></p>
                        <ul>
                          {openApiSpec.servers.map((server: any, idx: number) => (
                            <li key={idx}>
                              <code>{server.url}</code> - {server.description}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default APIDocumentation;
