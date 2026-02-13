
import { toast } from "react-toastify";
import React, { useState, useEffect } from "react";
import { adminAuthService } from "../services/adminAuthService";

const API_BASE = "http://localhost:8000/admin/kb";

interface DocumentItem {
  document_id: string;
  title: string;
  document_type: string;
  version: number;
  chunks: number;
}

const AdminDashboard: React.FC = () => {
  const [adminName, setAdminName] = useState("Admin");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("admin_token");

  // 👤 Get admin name
  useEffect(() => {
    const fetchAdmin = async () => {
      try {
        const admin = await adminAuthService.getMe();
        setAdminName(admin.username);
      } catch (error) {
        console.error("Failed to fetch admin info");
      }
    };

    fetchAdmin();
    fetchDocuments();
  }, []);

  //  Fetch Documents from Backend
  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE}/documents`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      setDocuments(data);
    } catch (error) {
      console.error("Failed to fetch documents");
    }
  };

  //  Upload
  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("document_type", "POLICY");
    formData.append("industry", "general");
    formData.append("language", "en");

    try {
      setLoading(true);

      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail);
      }

      toast.success("PDF uploaded successfully ");
      setSelectedFile(null);
      fetchDocuments();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete
  const handleDelete = async (documentId: string) => {
    try {
      await fetch(`${API_BASE}/${documentId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      fetchDocuments();
    } catch (error) {
      console.error("Delete failed");
    }
  };

  // // 👁 Show (Metadata only – file stored temp)
  // const handleShow = (doc: DocumentItem) => {
  //   alert(
  //     `Title: ${doc.title}\nType: ${doc.document_type}\nChunks: ${doc.chunks}`
  //   );
  // };

  // 🚪 Logout
  const handleLogout = () => {
    adminAuthService.logout();
    window.location.href = "/admin-login";
  };

  return (
    <div className="min-h-screen bg-[#0d0d0d] text-white p-8">
      
      {/* 🔝 Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>

        <div className="flex items-center gap-6">
          <span className="text-gray-300">
            Hello, <span className="font-semibold">{adminName}</span>
          </span>
          <button
            onClick={handleLogout}
            className="bg-red-500 px-4 py-2 rounded-lg hover:bg-red-600 transition"
          >
            Logout
          </button>
        </div>
      </div>

      {/* 📂 Upload Section */}
      <div className="bg-[#171717] p-6 rounded-2xl shadow-lg border border-[#303030] mb-8">
        <h2 className="text-lg font-semibold mb-4">
          Upload Knowledge Base PDF
        </h2>

        <div className="flex gap-4 items-center">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) =>
              setSelectedFile(e.target.files ? e.target.files[0] : null)
            }
            className="text-sm"
          />

          <button
            onClick={handleUpload}
            className="bg-white text-black px-6 py-2 rounded-lg hover:bg-gray-300 transition"
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
        </div>
      </div>

      {/* 📄 Uploaded Documents List */}
      <div className="bg-[#171717] p-6 rounded-2xl shadow-lg border border-[#303030]">
        <h2 className="text-lg font-semibold mb-4">
          Uploaded Documents
        </h2>

        {documents.length === 0 ? (
          <p className="text-gray-400">No documents uploaded yet.</p>
        ) : (
          <ul className="space-y-3">
            {documents.map((doc) => (
              <li
                key={doc.document_id}
                className="flex justify-between items-center bg-[#212121] p-3 rounded-lg"
              >
                <span>{doc.title}</span>

                <div className="flex gap-3">
                  {/* <button
                    onClick={() => handleShow(doc)}
                    className="bg-blue-500 px-3 py-1 rounded-md text-sm hover:bg-blue-600 transition"
                  >
                    Show
                  </button> */}

                  <button
                    onClick={() => handleDelete(doc.document_id)}
                    className="bg-red-500 px-3 py-1 rounded-md text-sm hover:bg-red-600 transition"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

    </div>
  );
};

export default AdminDashboard;
