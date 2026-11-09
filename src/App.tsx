import { AuthProvider } from './context/AuthContext';
import { MaintenanceProvider } from './context/MaintenanceContext';
import { Site404Provider } from './context/Site404Context';
import { BrandingProvider } from './context/BrandingContext';
import { Root } from './SystemApp';
import AppDialogs from './components/ui/AppDialogs';

export default function App() {
  return (
    <AuthProvider>
      <BrandingProvider>
        <MaintenanceProvider>
          <Site404Provider>
            <Root />
            <AppDialogs />
          </Site404Provider>
        </MaintenanceProvider>
      </BrandingProvider>
    </AuthProvider>
  );
}
