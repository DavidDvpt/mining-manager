import MainLayout from '@/layouts/mainLayout/MainLayout';
import { Panel, Section } from '@/shared/components';

/** Render the transactions page shell with a temporary page marker. */
export function TransactionPage() {
  return (
    <MainLayout>
      <Panel>
        <Section>
          <h1>Transactions</h1>
        </Section>
      </Panel>
    </MainLayout>
  );
}

export default TransactionPage;
