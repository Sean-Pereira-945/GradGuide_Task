import { useState, useEffect } from 'react'
import './styles.css'

function App() {
  const [activeTab, setActiveTab] = useState('jobs')
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [jobTypeFilter, setJobTypeFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [cityFilter, setCityFilter] = useState('')
  const [selectedJob, setSelectedJob] = useState(null)

  // Profile & Reminders
  const [profile, setProfile] = useState({
    country: 'Australia',
    visa_type: 'Student (Subclass 500)',
    current_weekly_hours: 12.0,
    in_study_period: true,
    home_city: 'Adelaide',
  })

  const [applications, setApplications] = useState([])
  const [reminders, setReminders] = useState([])

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (searchQuery) params.append('q', searchQuery)
      if (jobTypeFilter) params.append('job_type', jobTypeFilter)
      if (categoryFilter) params.append('category', categoryFilter)
      if (cityFilter) params.append('city', cityFilter)

      const res = await fetch(`/api/jobs?${params.toString()}`)
      const data = await res.json()
      setJobs(data.data || [])
    } catch (err) {
      console.error('Failed to fetch jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchProfile = async () => {
    try {
      const res = await fetch('/api/profile')
      const data = await res.json()
      if (data && !data.error) setProfile(data)
    } catch (err) {
      console.error('Failed to fetch profile:', err)
    }
  }

  const fetchApplications = async () => {
    try {
      const res = await fetch('/api/applications')
      const data = await res.json()
      setApplications(data.data || [])

      const remRes = await fetch('/api/applications/reminders')
      const remData = await remRes.json()
      setReminders(remData.due_reminders || [])
    } catch (err) {
      console.error('Failed to fetch applications:', err)
    }
  }

  useEffect(() => {
    fetchJobs()
    fetchProfile()
    fetchApplications()
  }, [jobTypeFilter, categoryFilter, cityFilter])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    fetchJobs()
  }

  const handleUpdateProfile = async (e) => {
    e.preventDefault()
    try {
      await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      })
      alert('Student Profile Updated!')
    } catch (err) {
      console.error('Failed to update profile:', err)
    }
  }

  const handleTrackJob = async (jobId, status = 'saved') => {
    try {
      await fetch('/api/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          status,
          applied_on: new Date().toISOString().split('T')[0],
          follow_up_on: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
          notes: 'Saved from GradGuide',
        }),
      })
      fetchApplications()
      alert(`Job marked as ${status}!`)
    } catch (err) {
      console.error('Failed to track job:', err)
    }
  }

  const computeVisaStatus = (job) => {
    if (!profile.in_study_period) {
      return { status: 'ok', badge: 'Study Break (Unlimited Hours)', class: 'badge-ok' }
    }
    // Extract job hours limit
    const jobHours = job.hours_max || 15.0
    const totalWeekly = profile.current_weekly_hours + jobHours
    const fortnightly = totalWeekly * 2

    if (fortnightly > 48.0) {
      return {
        status: 'over_cap',
        badge: `Exceeds Cap (${fortnightly}h/fortnight)`,
        class: 'badge-danger',
        msg: `Adding ~${jobHours}h/wk to your ${profile.current_weekly_hours}h/wk totals ${fortnightly}h/fortnight, exceeding the 48h visa cap!`,
      }
    } else if (fortnightly >= 44.0) {
      return {
        status: 'warning',
        badge: `Near Cap (${fortnightly}h/fortnight)`,
        class: 'badge-warning',
        msg: `Brings total to ${fortnightly}h/fortnight, approaching your 48h limit.`,
      }
    }
    return {
      status: 'ok',
      badge: `Visa OK (${fortnightly}h/fortnight)`,
      class: 'badge-ok',
      msg: `Total work (${fortnightly}h/fortnight) is comfortably within your 48h visa work cap.`,
    }
  }

  const [refreshing, setRefreshing] = useState(false)

  const handleLiveScrapeRefresh = async () => {
    setRefreshing(true)
    try {
      const scrapeCity = cityFilter || profile.home_city
      const params = scrapeCity ? `?city=${encodeURIComponent(scrapeCity)}` : ''
      const res = await fetch(`/api/jobs/refresh-live${params}`, { method: 'POST' })
      const data = await res.json()
      alert(data.message || 'Live scrape updated real-time data!')
      fetchJobs()
    } catch (err) {
      console.error('Failed to run live scrape:', err)
      alert('Error triggering live scrape.')
    } finally {
      setRefreshing(false)
    }
  }

  return (
    <main className="app-shell">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href="/" onClick={(e) => { e.preventDefault(); setActiveTab('jobs'); }}>
          <span className="brand-mark">G</span>
          <span>GradGuide</span>
        </a>
        <div className="nav-links">
          <button className={activeTab === 'jobs' ? 'active' : ''} onClick={() => setActiveTab('jobs')}>
            Find Work
          </button>
          <button className={activeTab === 'tracker' ? 'active' : ''} onClick={() => setActiveTab('tracker')}>
            Applications ({applications.length})
          </button>
          <button className={activeTab === 'profile' ? 'active' : ''} onClick={() => setActiveTab('profile')}>
            My Profile & Visa
          </button>
          <button className="btn-live-scrape" onClick={handleLiveScrapeRefresh} disabled={refreshing}>
            {refreshing ? '🔄 Scraping Web Live...' : '⚡ Fetch Real-Time Data'}
          </button>
        </div>
      </nav>

      {/* Reminder Banner */}
      {reminders.length > 0 && (
        <div className="reminder-banner">
          🔔 <strong>Follow-up Reminder:</strong> You have {reminders.length} job application(s) due for follow-up today!
        </div>
      )}

      {/* JOBS TAB */}
      {activeTab === 'jobs' && (
        <>
          <section className="hero">
            <div className="hero-copy">
              <p className="eyebrow">International Student Job Discovery</p>
              <h1>Find work that fits your student visa.</h1>
              <p className="hero-description">
                Search part-time, casual, full-time and internship roles with real-time visa work-hour alerts and transparent trust signals.
              </p>
              <form className="search-field" onSubmit={handleSearchSubmit}>
                <span className="search-icon">⌕</span>
                <input
                  type="search"
                  placeholder="Search by title, employer, e.g. 'Barista', 'Library', 'Retail'"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button type="submit" className="btn-primary">Search</button>
              </form>

              {/* Filters */}
              <div className="filter-bar">
                <select value={jobTypeFilter} onChange={(e) => setJobTypeFilter(e.target.value)}>
                  <option value="">All Job Types</option>
                  <option value="casual">Casual</option>
                  <option value="part_time">Part-Time</option>
                  <option value="internship">Internship</option>
                  <option value="full_time">Full-Time</option>
                </select>

                <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
                  <option value="">All Categories</option>
                  <option value="cafe">Cafe / Hospitality</option>
                  <option value="retail">Retail / Supermarket</option>
                  <option value="tutoring">Tutoring / Academic</option>
                  <option value="tech">Tech / Software</option>
                </select>

                <select value={cityFilter} onChange={(e) => setCityFilter(e.target.value)}>
                  <option value="">All Cities</option>
                  <option value="Adelaide">Adelaide</option>
                  <option value="Melbourne">Melbourne</option>
                  <option value="Sydney">Sydney</option>
                  <option value="Brisbane">Brisbane</option>
                  <option value="Perth">Perth</option>
                  <option value="Canberra">Canberra</option>
                </select>
              </div>
            </div>
          </section>

          <section className="workspace">
            <div className="section-heading">
              <h2>Available Job Listings</h2>
              <span className="result-count">{jobs.length} roles found</span>
            </div>

            {loading ? (
              <p>Loading listings...</p>
            ) : (
              <div className="job-list">
                {jobs.map((job) => {
                  const visaInfo = computeVisaStatus(job)
                  return (
                    <article className="job-card-wrapper" key={job.id}>
                      <div className="job-row" onClick={() => setSelectedJob(job)}>
                        <div className="job-main">
                          <h3>{job.title}</h3>
                          <p>{job.employer || 'Unlisted Employer'} · {job.location_text}</p>
                        </div>
                        <div className="job-meta">
                          <span className={`badge ${visaInfo.class}`}>{visaInfo.badge}</span>
                          <span className="badge badge-trust">Trust: {job.trust_score}%</span>
                          <strong>{job.pay_text || 'Pay listed in description'}</strong>
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        </>
      )}

      {/* DETAIL MODAL / DRAWER */}
      {selectedJob && (
        <div className="modal-overlay" onClick={() => setSelectedJob(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedJob(null)}>✕</button>
            <h2>{selectedJob.title}</h2>
            <p className="employer-subtitle">{selectedJob.employer} — {selectedJob.location_text}</p>
            <p><strong>Pay Rate:</strong> {selectedJob.pay_text || 'Standard award rate'}</p>

            <div className="detail-section">
              <h4>Visa Work-Cap Guidance</h4>
              <p>{computeVisaStatus(selectedJob).msg}</p>
            </div>

            <div className="detail-section">
              <h4>Employer Trust Signals ({selectedJob.trust_score}%)</h4>
              <ul>
                {selectedJob.trust_reasons?.map((reason, idx) => (
                  <li key={idx}>✓ {reason}</li>
                ))}
              </ul>
            </div>

            <div className="detail-section">
              <h4>Description</h4>
              <p>{selectedJob.description}</p>
            </div>

            <div className="modal-actions">
              <button className="btn-primary" onClick={() => handleTrackJob(selectedJob.id, 'applied')}>Mark as Applied</button>
              <button className="btn-secondary" onClick={() => handleTrackJob(selectedJob.id, 'saved')}>Save for Later</button>
              <a href={selectedJob.url} target="_blank" rel="noreferrer" className="btn-link">View Original Listing ↗</a>
            </div>
          </div>
        </div>
      )}

      {/* TRACKER TAB */}
      {activeTab === 'tracker' && (
        <section className="workspace">
          <h2>Application Tracker ({applications.length})</h2>
          <p>Keep track of saved, applied, and interview roles with follow-up dates.</p>
          <div className="tracker-list">
            {applications.map((app) => (
              <div className="tracker-card" key={app.id}>
                <div>
                  <h3>{app.title}</h3>
                  <p>{app.employer} · Status: <strong>{app.status.toUpperCase()}</strong></p>
                  <p><small>Follow-up scheduled for: {app.follow_up_on || 'Not set'}</small></p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* PROFILE TAB */}
      {activeTab === 'profile' && (
        <section className="workspace">
          <h2>Student Profile & Visa Settings</h2>
          <form className="profile-form" onSubmit={handleUpdateProfile}>
            <label>
              Country of Study:
              <input type="text" value={profile.country} onChange={(e) => setProfile({ ...profile, country: e.target.value })} />
            </label>
            <label>
              Visa Subclass:
              <input type="text" value={profile.visa_type} onChange={(e) => setProfile({ ...profile, visa_type: e.target.value })} />
            </label>
            <label>
              Current Weekly Work Commitment (Hours/Week):
              <input type="number" step="0.5" value={profile.current_weekly_hours} onChange={(e) => setProfile({ ...profile, current_weekly_hours: parseFloat(e.target.value) || 0 })} />
            </label>
            <label className="checkbox-label">
              <input type="checkbox" checked={profile.in_study_period} onChange={(e) => setProfile({ ...profile, in_study_period: e.target.checked })} />
              Currently in Study Period (Uncheck during official semester breaks)
            </label>
            <button type="submit" className="btn-primary">Save Settings</button>
          </form>
        </section>
      )}

      <footer>
        <p>Visa & Trust information is decision support guidance, not legal advice. Always verify on official government pages.</p>
      </footer>
    </main>
  )
}

export default App
