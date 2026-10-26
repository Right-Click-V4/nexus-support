import { AuthProvider } from './context/AuthContext';
import { MaintenanceProvider } from './context/MaintenanceContext';
import { Site404Provider } from './context/Site404Context';
import { BrandingProvider } from './context/BrandingContext';
import { Root } from './SystemApp';

export default function App() {
  return (
    <AuthProvider>
      <BrandingProvider>
        <MaintenanceProvider>
          <Site404Provider>
            <Root />
          </Site404Provider>
        </MaintenanceProvider>
      </BrandingProvider>
    </AuthProvider>
  );
}
