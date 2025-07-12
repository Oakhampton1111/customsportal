# Professional Component Library

This directory contains a comprehensive professional component library designed for the Customs Broker Portal. These components extend the existing design system with enterprise-grade patterns optimized for data-dense broker workflows.

## Component Categories

### 1. Data Display Components

#### ProfessionalCard
Enhanced card component with multiple variants for different data types.

```tsx
import { ProfessionalCard } from './ui';

// Intelligence card with items
<ProfessionalCard variant="intelligence" title="Tariff Analysis">
  <ProfessionalCard.Items>
    <ProfessionalCard.Item label="Classification" value="8471.30.01" />
    <ProfessionalCard.Item label="Duty Rate" value="5%" />
  </ProfessionalCard.Items>
</ProfessionalCard>

// KPI card with trend
<ProfessionalCard variant="kpi" title="Total Duties" trend="up">
  <ProfessionalCard.Value>$45,230</ProfessionalCard.Value>
  <ProfessionalCard.Change>+12.5%</ProfessionalCard.Change>
</ProfessionalCard>
```

#### KPICard
Specialized components for displaying key performance indicators with trends and responsive grids.

```tsx
import { KPICard } from './ui';

<KPICard.Grid>
  <KPICard
    title="Monthly Clearances"
    value="1,247"
    change="+8.2%"
    trend="up"
    color="blue"
  />
  <KPICard
    title="Average Processing Time"
    value="2.3 days"
    change="-0.5 days"
    trend="down"
    color="green"
  />
</KPICard.Grid>
```

#### IntelligencePanel
Reusable components for displaying synthesized intelligence data.

```tsx
import { IntelligencePanel } from './ui';

<IntelligencePanel title="Trade Intelligence Summary">
  <IntelligencePanel.Items>
    <IntelligencePanel.Item
      label="Recommended Classification"
      value="8471.30.01"
      confidence="95%"
    />
  </IntelligencePanel.Items>
  <IntelligencePanel.Summary>
    Based on product description and historical data
  </IntelligencePanel.Summary>
</IntelligencePanel>
```

### 2. Data Input Components

#### ProfessionalForm
Enhanced form components with professional styling, validation states, and accessibility features.

```tsx
import { ProfessionalForm } from './ui';

<ProfessionalForm onSubmit={handleSubmit}>
  <ProfessionalForm.Section title="Product Information">
    <ProfessionalForm.Field
      label="Product Description"
      name="description"
      required
      validation={{ required: 'Description is required' }}
    />
    <ProfessionalForm.Select
      label="Country of Origin"
      name="origin"
      options={countries}
    />
  </ProfessionalForm.Section>
  <ProfessionalForm.Actions>
    <ProfessionalForm.Button type="submit" variant="primary">
      Submit
    </ProfessionalForm.Button>
  </ProfessionalForm.Actions>
</ProfessionalForm>
```

#### ProfessionalFilters
Advanced filtering components with multiple filter types and layouts.

```tsx
import { ProfessionalFilters, QuickFilters, SearchBar } from './ui';

const filters = [
  {
    key: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Active', value: 'active', count: 45 },
      { label: 'Pending', value: 'pending', count: 12 }
    ]
  },
  {
    key: 'dateRange',
    label: 'Date Range',
    type: 'daterange'
  }
];

<ProfessionalFilters
  filters={filters}
  values={filterValues}
  onChange={setFilterValues}
  layout="grid"
/>
```

### 3. Data Tables

#### ProfessionalTable
Enterprise-grade table component with sorting, filtering, pagination, and selection.

```tsx
import { ProfessionalTable, DataTable } from './ui';

const columns = [
  {
    key: 'id',
    title: 'Entry ID',
    sortable: true,
    width: '120px'
  },
  {
    key: 'description',
    title: 'Description',
    filterable: true,
    render: (value, record) => (
      <div className="font-medium">{value}</div>
    )
  }
];

<ProfessionalTable
  data={entries}
  columns={columns}
  rowKey="id"
  pagination={{
    current: page,
    pageSize: 20,
    total: totalEntries,
    onChange: handlePageChange
  }}
  selection={{
    selectedRowKeys: selected,
    onChange: setSelected
  }}
/>
```

### 4. Layout Components

#### Advanced Layouts
Sophisticated layout patterns for complex data presentation.

```tsx
import { 
  SplitPanel, 
  MasterDetail, 
  TabPanel, 
  Accordion, 
  GridLayout 
} from './ui';

// Split panel with resizable divider
<SplitPanel
  left={<TariffTree />}
  right={<TariffDetails />}
  resizable
  leftWidth="300px"
/>

// Master-detail with responsive behavior
<MasterDetail
  masterList={<EntryList />}
  detailView={<EntryDetails />}
  masterWidth="400px"
  responsive
/>

// Tab panel with badges
<TabPanel
  tabs={[
    { id: 'overview', label: 'Overview', content: <Overview /> },
    { id: 'duties', label: 'Duties', content: <Duties />, badge: '5' }
  ]}
  activeTab={activeTab}
  onTabChange={setActiveTab}
/>
```

### 5. Action Components

#### ActionToolbar
Comprehensive toolbar for bulk operations and quick actions.

```tsx
import { ActionToolbar, BulkActions, QuickActions, commonActions } from './ui';

const actions = [
  { ...commonActions.export, onClick: handleExport },
  { ...commonActions.delete, onClick: handleDelete },
  {
    id: 'classify',
    label: 'Auto-Classify',
    icon: <FiZap />,
    onClick: handleClassify,
    variant: 'primary'
  }
];

<ActionToolbar
  actions={actions}
  selectedCount={selectedEntries.length}
  totalCount={totalEntries}
  onSelectAll={handleSelectAll}
  onClearSelection={handleClearSelection}
/>
```

### 6. Modal Components

#### Professional Modals and Dialogs
Enterprise-grade modal components for various use cases.

```tsx
import { 
  Modal, 
  Dialog, 
  ConfirmDialog, 
  FormDialog, 
  Drawer 
} from './ui';

// Confirmation dialog
<ConfirmDialog
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  onConfirm={handleDelete}
  title="Delete Entry"
  message="Are you sure you want to delete this entry? This action cannot be undone."
  type="danger"
/>

// Form dialog
<FormDialog
  isOpen={showForm}
  onClose={() => setShowForm(false)}
  onSubmit={handleSubmit}
  title="Create New Entry"
  size="large"
>
  <FormFields />
</FormDialog>

// Side drawer
<Drawer
  isOpen={showDrawer}
  onClose={() => setShowDrawer(false)}
  title="Entry Details"
  position="right"
  size="large"
>
  <EntryDetails />
</Drawer>
```

## Design Principles

### 1. Professional Aesthetics
- Clean, modern design with consistent spacing and typography
- Corporate blue color palette with semantic color coding
- High information density optimized for broker workflows

### 2. Accessibility
- Full keyboard navigation support
- ARIA labels and semantic HTML
- Screen reader compatibility
- Focus management and visual indicators

### 3. Responsive Design
- Mobile-first approach with progressive enhancement
- Adaptive layouts that work across all screen sizes
- Touch-friendly interactions on mobile devices

### 4. Performance
- Optimized rendering with React best practices
- Lazy loading for large datasets
- Efficient state management and updates

### 5. Extensibility
- Modular component architecture
- Consistent prop interfaces
- Easy customization through className and style props

## Usage Guidelines

### Import Strategy
```tsx
// Import specific components
import { ProfessionalCard, KPICard } from '@/components/ui';

// Or import from category-specific files
import { ProfessionalTable } from '@/components/ui/ProfessionalTable';
```

### Styling Integration
All components integrate seamlessly with the existing design system:
- Use Tailwind CSS classes for customization
- Leverage the modern-enterprise.css design tokens
- Follow established color and spacing patterns

### State Management
Components are designed to work with various state management patterns:
- Local component state for simple interactions
- Context providers for shared state
- External state management libraries (Redux, Zustand, etc.)

### TypeScript Support
Full TypeScript support with comprehensive type definitions:
- Strongly typed props and interfaces
- Generic components for type safety
- IntelliSense support in IDEs

## Best Practices

### 1. Component Composition
Prefer composition over configuration:
```tsx
// Good: Composable structure
<ProfessionalCard variant="intelligence">
  <ProfessionalCard.Header>
    <ProfessionalCard.Title>Analysis</ProfessionalCard.Title>
    <ProfessionalCard.Actions>
      <Button size="small">Refresh</Button>
    </ProfessionalCard.Actions>
  </ProfessionalCard.Header>
  <ProfessionalCard.Content>
    <ProfessionalCard.Items>
      <ProfessionalCard.Item label="Status" value="Complete" />
    </ProfessionalCard.Items>
  </ProfessionalCard.Content>
</ProfessionalCard>
```

### 2. Data Handling
Use proper data structures and validation:
```tsx
// Define clear interfaces
interface TariffEntry {
  id: string;
  code: string;
  description: string;
  dutyRate: number;
  status: 'active' | 'pending' | 'archived';
}

// Use with table components
<ProfessionalTable<TariffEntry>
  data={entries}
  columns={columns}
  rowKey="id"
/>
```

### 3. Error Handling
Implement proper error boundaries and loading states:
```tsx
<ProfessionalTable
  data={entries}
  columns={columns}
  loading={isLoading}
  emptyText="No entries found"
/>
```

### 4. Performance Optimization
Use React optimization techniques:
```tsx
// Memoize expensive calculations
const processedData = useMemo(() => 
  processEntries(rawData), [rawData]
);

// Optimize callbacks
const handleSelect = useCallback((selectedKeys) => {
  setSelected(selectedKeys);
}, []);
```

## Migration Guide

### From Existing Components
When migrating from existing components to the professional library:

1. **Card Components**: Replace `Card` with `ProfessionalCard` for enhanced features
2. **Form Components**: Upgrade to `ProfessionalForm` for better validation and styling
3. **Table Components**: Use `ProfessionalTable` for advanced data management
4. **Layout Components**: Leverage new layout patterns for complex interfaces

### Gradual Adoption
The professional components are designed for gradual adoption:
- Start with high-impact areas like the Dashboard
- Migrate page by page to maintain stability
- Use both old and new components during transition

## Contributing

When adding new components to the professional library:

1. Follow the established naming conventions
2. Include comprehensive TypeScript types
3. Add proper documentation and examples
4. Ensure accessibility compliance
5. Test across different screen sizes
6. Update the index.ts export file

## Support

For questions or issues with the professional component library:
- Check the component documentation and examples
- Review the existing codebase for usage patterns
- Follow the established design system guidelines