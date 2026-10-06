"""Panel derecho: servicio, compras, concurrencia, cocineros y registro."""

import time
import tkinter as tk
from tkinter import ttk

from .tema import FONDO, ROJO, TEXTO


class PanelControl:
    def __init__(self, master, cocineros, colores, opciones_compra, unidades_compra,
                 al_abrir, al_cambiar_modo, al_comprar):
        self._al_abrir = al_abrir
        self._al_cambiar_modo = al_cambiar_modo
        self.frame = p = tk.Frame(master, bg=FONDO)

        f = ttk.LabelFrame(p, text="Servicio")
        f.pack(fill="x", pady=(0, 6))
        self.lbl_servicio = tk.Label(f, font=("Helvetica", 12, "bold"), bg=FONDO,
                                     anchor="w")
        self.lbl_servicio.pack(fill="x", padx=6)
        self.lbl_marcador = tk.Label(f, font=("Helvetica", 11), bg=FONDO, anchor="w")
        self.lbl_marcador.pack(fill="x", padx=6)
        self.btn_abrir = ttk.Button(f, text="Abrir servicio", command=self._abrir,
                                    state="disabled")
        self.btn_abrir.pack(fill="x", padx=6, pady=4)
        self.var_inseguro = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="Modo SIN sincronización (ver errores)",
                        variable=self.var_inseguro,
                        command=self._cambiar_modo).pack(anchor="w", padx=6, pady=(0, 4))

        f = ttk.LabelFrame(p, text=f"Despensa: comprar {unidades_compra} unidades")
        f.pack(fill="x", pady=6)
        for k, (ing, costo) in enumerate(opciones_compra):
            ttk.Button(f, text=f"{ing}  ${costo}", width=13,
                       command=lambda i=ing: al_comprar(i)
                       ).grid(row=k // 3, column=k % 3, padx=3, pady=3)

        f = ttk.LabelFrame(p, text="Panel de concurrencia")
        f.pack(fill="x", pady=6)
        self.lbl_conc = tk.Label(f, font=("Menlo", 10), bg=FONDO, justify="left",
                                 anchor="w")
        self.lbl_conc.pack(fill="x", padx=6, pady=2)

        f = ttk.LabelFrame(p, text="Cocineros (hilos)")
        f.pack(fill="x", pady=6)
        self.lbl_coc = {}
        for nombre in cocineros:
            l = tk.Label(f, text=f"{nombre}: …", fg=colores[nombre], bg=FONDO,
                         anchor="w", font=("Helvetica", 10, "bold"), wraplength=380,
                         justify="left")
            l.pack(fill="x", padx=6)
            self.lbl_coc[nombre] = l

        f = ttk.LabelFrame(p, text="Registro")
        f.pack(fill="both", pady=6)
        self.txt = tk.Text(f, width=52, height=6, font=("Helvetica", 10),
                           bg="white", relief="flat", wrap="word")
        self.txt.pack(fill="both", padx=4, pady=4)

    def grid(self, **opciones):
        self.frame.grid(**opciones)

    # ---------- acciones del usuario ----------
    def _abrir(self):
        self.btn_abrir.configure(state="disabled")
        self._al_abrir()

    def _cambiar_modo(self):
        self._al_cambiar_modo(not self.var_inseguro.get())

    # ---------- lo que piden los eventos ----------
    def habilitar_abrir(self, servicio):
        self.btn_abrir.configure(state="normal", text=f"Abrir servicio {servicio}")

    def estado_cocinero(self, nombre, texto):
        self.lbl_coc[nombre].configure(text=f"{nombre}: {texto}")

    def escribir(self, texto):
        self.txt.insert("end", texto + "\n")
        self.txt.see("end")

    # ---------- refresco periódico ----------
    def actualizar(self, foto):
        if foto.abierto:
            resto = max(0, foto.fin_servicio - time.time())
            estado = (f"Servicio {foto.servicio}/{foto.n_servicios}  ·  "
                      f"quedan {resto:4.0f} s")
        else:
            estado = f"Servicio {foto.servicio}/{foto.n_servicios}  ·  cocina cerrada"
        self.lbl_servicio.configure(text=estado)
        self.lbl_marcador.configure(
            text=f"Dinero: ${foto.dinero}   Entregados: {foto.entregados}   "
                 f"Perdidos: {foto.perdidos}",
            fg=ROJO if foto.dinero < 0 else TEXTO)

        lineas = []
        for est in foto.estaciones.values():
            cola = ", ".join(est.esperando) if est.esperando else "-"
            lineas.append(f"{est.etiqueta[:15]:<15} usados {est.usados}/{est.capacidad}  "
                          f"contador sem={est.contador_semaforo}  cola: {cola}")
        lineas.append(f"Lock despensa   {foto.dueno_despensa or 'libre'}")
        lineas.append(f"Lock caja       {foto.dueno_caja or 'libre'}")
        bi, bf = foto.barrera_inicio, foto.barrera_fin
        lineas.append(f"Barrera inicio  {bi.esperando}/{bi.partes} esperando")
        lineas.append(f"Barrera cierre  {bf.esperando}/{bf.partes} esperando")
        lineas.append(f"Event servicio  {'ABIERTO' if foto.abierto else 'cerrado'}")
        lineas.append(f"Hilos vivos     {foto.hilos_vivos}")
        viol = foto.violaciones
        lineas.append(f"Violaciones     {viol}"
                      + ("   <- ¡errores de concurrencia!" if viol else ""))
        self.lbl_conc.configure(text="\n".join(lineas), fg=ROJO if viol else TEXTO)
