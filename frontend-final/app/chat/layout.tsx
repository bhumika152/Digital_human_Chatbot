import Sidebar from "../../components/chat/Sidebar";
import TopProfileMenu from "@/components/TopProfileMenu";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar />

     <div
  style={{
    flex: 1,
    position: "relative",
    paddingTop: 60,
    backgroundColor: "black", // 🔥 THIS FIXES WHITE BAR
  }}
>

        
        {/* 🔝 TOP RIGHT */}
        <div style={{ position: "absolute", top: 12, right: 16, zIndex: 1000 }}>
          <TopProfileMenu />
        </div>

        {children}
      </div>
    </div>
  );
}
