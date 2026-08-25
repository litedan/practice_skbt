export type Role = 'employee' | 'hr' | 'admin'

export type RequestStatus = 'На рассмотрении' | 'Одобрено' | 'Отклонено' | 'Готово'

export type RequestItem = {
  id: number
  type: string
  period: string
  date: string
  status: RequestStatus
  comment?: string
}

export type DocumentItem = {
  id: number
  name: string
  date: string
  status: string
  needSign?: boolean
}

export type Employee = {
  id: number
  name: string
  email: string
  phone: string
  dept: string
  position: string
  manager: string
  hireDate: string
  city: string
  birthDate: string
}

export const currentUser = {
  name: 'Иванов И.И.',
  fullName: 'Иванов Иван Иванович',
  roleLabel: 'Менеджер · Отдел продаж',
  email: 'ivanov@company.ru',
  phone: '+7 (999) 123-45-67',
  dept: 'Отдел продаж',
  position: 'Менеджер',
  hireDate: '15.03.2022',
  birthDate: '12.04.1992',
  city: 'Москва',
  vacationDays: 14,
  // user_private_data
  passport: '4012 123456',
  inn: '770123456789',
  snils: '123-456-789 00',
  address: 'г. Москва, ул. Ленина, 10',
  militaryId: 'АБ 1234567',
  contractNumber: 'ТД-2022/118',
  // банк
  accountNumber: '40817810099910004312',
  bik: '044525225',
  bankName: 'ПАО Сбербанк',
  corrAccount: '30101810400000000225',
  kpp: '773601001',
}

export const requests: RequestItem[] = [
  {
    id: 124,
    type: 'Отпуск',
    period: '10.03 — 24.03.2026',
    date: '05.03.2026',
    status: 'На рассмотрении',
    comment: 'Семейная поездка',
  },
  {
    id: 118,
    type: 'Больничный',
    period: '01.02 — 05.02.2026',
    date: '01.02.2026',
    status: 'Одобрено',
  },
  {
    id: 110,
    type: 'Отпуск',
    period: '20.12 — 03.01.2026',
    date: '10.12.2025',
    status: 'Отклонено',
  },
  {
    id: 98,
    type: 'Справка 2-НДФЛ',
    period: '—',
    date: '20.01.2026',
    status: 'Готово',
  },
]

export const documents: DocumentItem[] = [
  {
    id: 1,
    name: 'Приказ о предоставлении отпуска',
    date: '05.03.2026',
    status: 'На подпись',
    needSign: true,
  },
  {
    id: 2,
    name: 'Заявление на отпуск',
    date: '05.03.2026',
    status: 'Подписан',
  },
  {
    id: 3,
    name: 'Справка 2-НДФЛ',
    date: '20.01.2026',
    status: 'Готов',
  },
]

export const notifications = [
  'Заявка на отпуск одобрена',
  'Новый документ на подпись',
]

export const hrRequests = [
  {
    employee: 'Иванов И.И.',
    type: 'Отпуск',
    period: '10.03—24.03',
    manager: 'Сидоров П.П.',
    status: 'На рассмотрении',
    canAct: true,
  },
  {
    employee: 'Козлова М.А.',
    type: 'Больничный',
    period: '01.02—05.02',
    manager: 'Сидоров П.П.',
    status: 'Одобрено рук.',
    canAct: true,
  },
  {
    employee: 'Смирнов А.В.',
    type: 'Справка 2-НДФЛ',
    period: '—',
    manager: '—',
    status: 'Новая',
    canAct: true,
  },
  {
    employee: 'Орлова Е.Н.',
    type: 'Отпуск',
    period: '15.04—28.04',
    manager: 'Сидоров П.П.',
    status: 'Ожидает приказа',
    canAct: false,
  },
]

export const employees: Employee[] = [
  {
    id: 14,
    name: 'Иванов И.И.',
    email: 'ivanov@company.ru',
    phone: '+7 (999) 123-45-67',
    dept: 'Продажи',
    position: 'Менеджер',
    manager: 'Сидоров П.П.',
    hireDate: '15.03.2022',
    city: 'Москва',
    birthDate: '12.04.1992',
  },
  {
    id: 15,
    name: 'Козлова М.А.',
    email: 'kozlova@company.ru',
    phone: '+7 (999) 222-33-44',
    dept: 'Продажи',
    position: 'Специалист',
    manager: 'Сидоров П.П.',
    hireDate: '01.06.2023',
    city: 'Москва',
    birthDate: '03.11.1995',
  },
  {
    id: 16,
    name: 'Смирнов А.В.',
    email: 'smirnov@company.ru',
    phone: '+7 (999) 555-66-77',
    dept: 'IT',
    position: 'Разработчик',
    manager: 'Орлова Е.Н.',
    hireDate: '10.01.2021',
    city: 'Казань',
    birthDate: '22.08.1990',
  },
  {
    id: 17,
    name: 'Орлова Е.Н.',
    email: 'orlova@company.ru',
    phone: '+7 (999) 888-99-00',
    dept: 'IT',
    position: 'Руководитель',
    manager: '—',
    hireDate: '12.09.2018',
    city: 'Москва',
    birthDate: '14.02.1985',
  },
]

export const adminUsers = [
  {
    name: 'Иванов И.И.',
    email: 'ivanov@company.ru',
    dept: 'Продажи',
    role: 'Сотрудник',
    blocked: false,
  },
  {
    name: 'Петрова А.С.',
    email: 'petrova@company.ru',
    dept: 'HR',
    role: 'HR',
    blocked: false,
  },
  {
    name: 'Сидоров П.П.',
    email: 'sidorov@company.ru',
    dept: 'Продажи',
    role: 'Руководитель',
    blocked: false,
  },
  {
    name: 'Новиков К.Д.',
    email: 'novikov@company.ru',
    dept: 'IT',
    role: 'Сотрудник',
    blocked: true,
  },
]
