import { ChangeDetectionStrategy, Component, computed, input, signal } from '@angular/core';

const fields = [
  { key: 'codigo', label: 'Código', type: 'text', required: true },
  { key: 'nombre', label: 'Nombre', type: 'text', required: true },
  { key: 'categoria', label: 'Categoría', type: 'text', required: false },
  { key: 'precio_compra', label: 'Precio de compra', type: 'number', min: 0, step: '0.01', required: true },
  { key: 'precio_venta', label: 'Precio de venta', type: 'number', min: 0.01, step: '0.01', required: true },
  { key: 'stock', label: 'Existencias', type: 'number', min: 0, required: true },
  { key: 'stock_minimo', label: 'Stock mínimo', type: 'number', min: 0, required: true },
  { key: 'dias_entrega', label: 'Plazo de entrega en días', type: 'number', min: 0, max: 30, required: true },
] as const;

type Field = typeof fields[number]['key'];
type TextField = 'codigo' | 'nombre' | 'categoria';
type Product = Record<TextField, string> & Record<Exclude<Field, TextField>, number> & { id: number };
type Submit = (path: string, data: Record<string, string | number>) => Promise<boolean>;

@Component({
  selector: 'inventory-panel',
  templateUrl: './inventory.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InventoryComponent {
  readonly rows = input<readonly Product[]>([]);
  readonly submit = input<Submit>();
  readonly fields = fields;
  readonly search = signal('');
  readonly page = signal(0);
  readonly busy = signal(false);
  readonly selected = signal<Product | null>(null);
  readonly draft = signal<Partial<Record<Field, string | number>>>({});
  readonly pageSize = 12;
  readonly money = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
  readonly filtered = computed(() => {
    const term = this.search().trim().toLocaleLowerCase('es');
    return this.rows().filter(row =>
      [row.codigo, row.nombre, row.categoria].some(value => String(value ?? '').toLocaleLowerCase('es').includes(term)),
    );
  });
  readonly pages = computed(() => Math.max(1, Math.ceil(this.filtered().length / this.pageSize)));
  readonly current = computed(() => Math.min(this.page(), this.pages() - 1));
  readonly visible = computed(() => this.filtered().slice(this.current() * this.pageSize, (this.current() + 1) * this.pageSize));

  changeSearch(value: string) {
    this.search.set(value);
    this.page.set(0);
  }

  changeField(key: Field, value: string) {
    this.draft.update(draft => ({ ...draft, [key]: value }));
  }

  edit(product: Product | null) {
    this.selected.set(product);
    this.draft.set(product ? { ...product } : {});
    if (product) document.getElementById('inventory-editor')?.focus();
  }

  async save(event: SubmitEvent) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!(form instanceof HTMLFormElement)) return;
    const fields: Record<string, string | number> = {};
    for (const [key, value] of new FormData(form)) {
      if (typeof value === 'string') fields[key] = value;
    }
    const product = this.selected();
    if (product) fields['id'] = product.id;
    const saved = await this.run(product ? 'productos/editar' : 'productos/crear', fields);
    if (saved) this.edit(null);
  }

  async remove(product: Product) {
    if (!window.confirm('¿Eliminar el producto ' + product.nombre + '?')) return;
    const removed = await this.run('productos/eliminar', { id: product.id });
    if (removed && this.selected()?.id === product.id) this.edit(null);
  }

  private async run(path: string, data: Record<string, string | number>) {
    const submit = this.submit();
    if (this.busy() || !submit) return false;
    this.busy.set(true);
    try {
      return await submit(path, data);
    } finally {
      this.busy.set(false);
    }
  }
}
