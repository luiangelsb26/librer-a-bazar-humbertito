import { provideZonelessChangeDetection } from '@angular/core';
import { createCustomElement } from '@angular/elements';
import { createApplication } from '@angular/platform-browser';
import { InventoryComponent } from './inventory';

async function registerInventory() {
  const name = 'humbertito-inventory';
  if (customElements.get(name)) return;
  const app = await createApplication({ providers: [provideZonelessChangeDetection()] });
  customElements.define(name, createCustomElement(InventoryComponent, { injector: app.injector }));
}

void registerInventory().catch(error => {
  console.error('No se pudo iniciar el inventario de Angular.', error);
  window.dispatchEvent(new Event('humbertito-inventory-error'));
});
