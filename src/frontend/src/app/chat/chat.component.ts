import { Component, Inject, OnInit, PLATFORM_ID, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { ChangeDetectorRef } from '@angular/core';


@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterOutlet, HttpClientModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  @ViewChild('chatBody') chatBody!: ElementRef;
  mostrarModal: boolean = false;
  consentimientoCargado: boolean = false;
  escribiendo: boolean = false;
  nuevoMensaje: string = '';
  mensajes: { texto: string; tipo: 'usuario' | 'bot' }[] = [];
  seudonimo: string = '';
  password: string = '';
  consentimiento: boolean = false;
  conversacionFinalizada: boolean = false;
  modo: 'login' | 'registro' = 'login';

  idUsuario: number = 0;
  idConversacion: number = 0;
  conversaciones: any[] = [];
  bloqueado = false;


  constructor(@Inject(PLATFORM_ID) private platformId: Object, private http: HttpClient, private cdRef: ChangeDetectorRef) {}

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      const idGuardado = localStorage.getItem('usuario_id');

      if (idGuardado) {
        this.idUsuario = +idGuardado;
        this.mostrarModal = false; 
        this.obtenerConversacionesYElegirUltima(); 
      } else {
        const consentimiento = localStorage.getItem('consentimiento');
        this.mostrarModal = consentimiento !== 'aceptado'; 
      }

      this.consentimientoCargado = true;
    }
  }

  resetConsentimiento(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('consentimiento');
      location.reload();
    }
  }

  ngAfterViewChecked(): void {
    this.scrollAlFinal();
  }

  scrollAlFinal() {
    if (this.chatBody) {
      const el = this.chatBody.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }

  comprobarEnvio(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.enviarMensaje();
  
      setTimeout(() => {
        const textarea = document.querySelector('textarea[name="mensaje"]') as HTMLTextAreaElement;
        if (textarea) {
          textarea.style.height = 'auto';
        }
      }, 0);
    }
  }
  
  ajustarAltura(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  }
   
  enviarMensaje(): void {
    const texto = this.nuevoMensaje.trim();
    if (!texto || this.bloqueado || this.conversacionFinalizada) return;

    this.mensajes.push({ texto, tipo: 'usuario' });
    this.nuevoMensaje = '';
    this.escribiendo = true;
    this.bloqueado = true; 

    this.http.post<{ respuesta: string }>('http://localhost:8000/chat', {
      mensaje: texto,
      id_conversacion: this.idConversacion,
      id_usuario: this.idUsuario
    }).subscribe({
      next: (res) => {
        this.mensajes.push({ texto: res.respuesta, tipo: 'bot' });
        this.escribiendo = false;
        this.bloqueado = false; 
      },
      error: () => {
        this.mensajes.push({ texto: 'Error al conectar con el asistente.', tipo: 'bot' });
        this.escribiendo = false;
        this.bloqueado = false; 
      }
    });
  }

  toggleModo() {
    this.modo = this.modo === 'registro' ? 'login' : 'registro';
  }

  autenticar() {
    if (!this.seudonimo.trim() || !this.password.trim()) {
      alert('Por favor, completa todos los campos');
      return;
    }

    if (this.modo === 'registro') {
      if (!this.consentimiento) {
        alert('Debes aceptar el tratamiento de datos');
        return;
      }
      this.registrarse();
    } else {
      this.iniciarSesion();
    }
  }

  registrarse() {
    const payload = {
      seudonimo: this.seudonimo,
      password: this.password,
      consentimiento_tratamiento: true
    };

    this.http.post<any>('http://localhost:8000/inicio', payload).subscribe({
      next: res => {
        this.idUsuario = res.usuario.id;
        this.idConversacion = res.conversacion_id;
        localStorage.setItem('usuario_id', this.idUsuario.toString());
        this.mostrarModal = false;
      },
      error: err => {
        alert(err.error.detail || 'Error al registrar');
      }
    });
  }

  iniciarSesion() {
    const payload = {
      seudonimo: this.seudonimo,
      password: this.password
    };

    this.http.post<any>('http://localhost:8000/login', payload).subscribe({
      next: res => {
        this.idUsuario = res.usuario.id;
        localStorage.setItem('usuario_id', this.idUsuario.toString());
        this.mostrarModal = false;
      },
      error: err => {
        alert(err.error.detail || 'Error al iniciar sesión');
      }
    });
  }

  get headers() {
    return {
      headers: {
        'X-User-Id': this.idUsuario.toString()
      }
    };
  }

  obtenerConversacionesYElegirUltima() {
    this.http.get<any[]>(`http://localhost:8000/conversaciones/usuario`, this.headers).subscribe(res => {
      this.conversaciones = res;
      if (res.length > 0) {
        const ultima = res[0];
        this.idConversacion = ultima.id;
        this.conversacionFinalizada = !!ultima.cerrada;
        this.cargarHistorial(this.idConversacion);
      } else {
        this.mensajes = [];
        this.conversacionFinalizada = false;
        alert('No tienes conversaciones previas. Puedes comenzar una nueva conversación.');
      }
    });
  }

  cargarHistorial(id: number) {
    this.http.get<any[]>(`http://localhost:8000/conversacion/${id}`).subscribe(res => {
      this.mensajes = res.map(msg => ({
        texto: msg.contenido,
        tipo: msg.tipo
      }));
    });
  }

  cambiarConversacionId(id: number): void {
    this.idConversacion = id;
    this.cargarHistorial(id);
    this.mensajes = [];

    const conv = this.conversaciones.find(c => c.id === id);
    this.conversacionFinalizada = !!conv?.cerrada;
    this.cdRef.detectChanges();
  }

  crearNuevaConversacion(): void {
    this.http.post<any>('http://localhost:8000/conversaciones', {}, this.headers).subscribe({
      next: (res) => {
        this.idConversacion = res.id;
        this.mensajes = [];
        this.conversacionFinalizada = false;
        this.obtenerConversacionesYElegirUltima();
      },
      error: (err) => {
        console.error('Error al crear conversación:', err);
        alert('Error al crear nueva conversación');
      }
    });
  }

  finalizarConversacion(): void {
    if (!this.idConversacion || !this.idUsuario) return;

    this.http.post(`http://localhost:8000/conversaciones/${this.idConversacion}/finalizar`, {}, this.headers).subscribe({
      next: () => {
        this.mensajes.push({ texto: 'Conversación finalizada.', tipo: 'bot' });
        this.conversacionFinalizada = true;
        this.http.get<any[]>(`http://localhost:8000/conversaciones/usuario`, this.headers)
        .subscribe(c => this.conversaciones = c);
      },
      error: err => {
        alert(err.error.detail || 'Error al finalizar conversación');
      }
    });
  }

  exportarPDF(): void {
    const url = `http://localhost:8000/conversaciones/${this.idConversacion}/exportar`;

    this.http.get(url, { responseType: 'blob' }).subscribe(blob => {
      const a = document.createElement('a');
      const objectUrl = URL.createObjectURL(blob);
      a.href = objectUrl;
      a.download = `conversacion_${this.idConversacion}.pdf`;
      a.click();
      URL.revokeObjectURL(objectUrl);
    }, error => {
      alert(error.error.detail || 'No se pudo exportar la conversación');
    });
  }

}
