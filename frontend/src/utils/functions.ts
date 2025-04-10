import type { MasteryLevel, Goal } from '../types/models'

function removeNullValueKeys(obj: { [key: string]: string | null }): {
  [key: string]: string
} {
  return Object.fromEntries(Object.entries(obj).filter(([_, value]) => value !== null)) as {
    [key: string]: string
  }
}

export function getMasteryColorByValue(value: number, masteryLevels: MasteryLevel[]): string {
  const masteryLevel = masteryLevels.find(ml => ml.minValue <= value && ml.maxValue >= value)
  return masteryLevel ? masteryLevel.color : 'black'
}

export function urlStringFrom(
  queryParams: { [key: string]: string | null },
  options?: { path?: string; mode?: string }
): string {
  const path = options?.path || ''
  const prefix = path ? path + '?' : '?'

  // merge or replace
  const mode = options?.mode || 'replace'
  // merge: we keep the current query params and add new ones
  // replace: we discard the current query params and use new ones

  let finalParams = { ...queryParams }

  if (mode === 'merge') {
    const currentUrlParams = new URLSearchParams(window.location.search)
    const currentParams: { [key: string]: string } = {}
    currentUrlParams.forEach((value, key) => {
      currentParams[key] = value
    })
    finalParams = { ...currentParams, ...queryParams }
  }
  // if a key is null, remove it
  finalParams = removeNullValueKeys(finalParams)

  return (
    prefix +
    Object.keys(finalParams)
      .map(key => `${key}=${finalParams[key] ?? ''}`)
      .join('&')
  )
}

export function inferMastery(goal: any): {
  status: number
  trend: number
  title: string
  groupName: string
} {
  const firstValue = goal.observations[0]?.masteryValue
  const lastValue = goal.observations[goal.observations.length - 1]?.masteryValue

  return {
    status: goal.latestObservation?.masteryValue || 0,
    trend: lastValue - firstValue,
    title: `${goal.title}: ${goal.latestObservation?.masteryValue}`,
    groupName: goal.groupId.includes('-') ? goal.groupId : 'sosialt',
  }
}

export function findAverage(numbers: number[]): number {
  return numbers.reduce((sum, currentValue) => sum + currentValue, 0) / numbers.length
}
