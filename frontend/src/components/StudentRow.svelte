<script lang="ts">
  import SparklineChart from './SparklineChart.svelte'
  import MasteryLevelBadge from './MasteryLevelBadge-v2.svelte'
  import ObservationEdit from './ObservationEdit.svelte'
  import { dataStore } from '../stores/data'
  import type {
    Student as StudentType,
    Goal as GoalType,
    Observation as ObservationType,
  } from '../types/models'

  const { student } = $props<{ student: StudentType }>()
  let selectedGoal = $state<GoalType | null>(null)
  let isOpen = $state(false)
  const basisGroups = $derived(
    $dataStore.groups.filter(s => s.type === 'basis' && student.groupIds.includes(s.id))
  )
  const teachingGroups = $derived(
    $dataStore.groups.filter(s => s.type === 'teaching' && student.groupIds.includes(s.id))
  )

  const studentGoalsWithObservations = $derived(
    $dataStore.goals
      .filter((goal: GoalType) => student.goalIds.includes(goal.id))
      .map((goal: GoalType) => {
        const result: any = { ...goal }
        result.observations = $dataStore.observations
          .filter(o => o.goalId === goal.id && o.studentId === student.id)
          .sort((a, b) => {
            return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
          })
        result.latestObservation = result.observations[result.observations.length - 1]
        return result
      })
  )

  function openObservationModal(goal: GoalType) {
    selectedGoal = goal
  }

  function getGoalDescription(goal: GoalType) {
    const group = $dataStore.groups.find(g => g.id === goal.groupId)
    if (!group) return null
    return group.type === 'basis' ? 'Sosialt' : group.name
  }
</script>

<div class="row py-2 align-items-center mx-0 border-top {isOpen ? '' : 'border-bottom'} ">
  <div class="col-3">
    {student.name}
    <button class="btn border expand-student-button" onclick={() => (isOpen = !isOpen)}>
      <span class="ms-2 caret-icon {isOpen ? 'rotated' : ''}">&#9656;</span>
    </button>
  </div>
  <div class="col-6">
    <div class="d-flex gap-2 justify-content-start">
      {#each studentGoalsWithObservations as studentGoal}
        {#if studentGoal.observations.length}
          <MasteryLevelBadge {studentGoal} />
        {/if}
      {/each}
    </div>
  </div>
  <div class="col-1">
    {basisGroups.map(g => g.name).join(', ')}
  </div>
  <div class="col-1">
    {studentGoalsWithObservations.length} mål
  </div>
  <div class="col-1">
    <div class="d-flex gap-2 justify-content-center">
      <a href={`/students/${student.id}`} class="link-button">Detaljer</a>
    </div>
  </div>
</div>

{#if isOpen}
  {#each studentGoalsWithObservations as studentGoal}
    <div class="row align-items-center border-top py-1 mx-0 expanded-student-row">
      <div class="col-3">
        <span class="fw-medium" title={studentGoal.description}>
          {studentGoal.title} |
          {getGoalDescription(studentGoal)}
        </span>
      </div>
      <div
        class="col-6"
        title={studentGoal.title +
          ': \n' +
          studentGoal.observations.map((o: ObservationType) => o.masteryValue).join(', ')}
      >
        {#if studentGoal.observations.length}
          <div class="d-flex align-items-center">
            <MasteryLevelBadge {studentGoal} />
            {#if studentGoal.observations.length > 1}
              <div class="chart-container ms-2">
                <SparklineChart
                  data={studentGoal.observations.map((o: ObservationType) => o.masteryValue)}
                  lineColor="rgb(100, 100, 100)"
                  label={studentGoal.title}
                />
              </div>
            {/if}
          </div>
        {:else}
          <div class="text-muted small">Ikke nok data</div>
        {/if}
      </div>
      <div class="col-1">
        <button
          class="link-button px-3"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#observationOffcanvas"
          aria-controls="observationOffcanvas"
          onclick={() => openObservationModal(studentGoal)}
        >
          +
        </button>
      </div>

      <div class="col-1"></div>
      <div class="col-1"></div>
    </div>
  {/each}

  {#if studentGoalsWithObservations.length === 0}
    <div class="text-center text-muted py-2">Ingen mål registrert</div>
  {/if}
{/if}

<!-- Single offcanvas for observations that gets reused -->
<div
  class="offcanvas offcanvas-end offcanvas-wide"
  data-bs-scroll="true"
  tabindex="-1"
  id="observationOffcanvas"
  aria-labelledby="observationOffcanvasLabel"
>
  {#if selectedGoal}
    <div class="offcanvas-header">
      <h5 class="offcanvas-title" id="observationOffcanvasLabel">
        Ny observasjon: {selectedGoal.title}
      </h5>
      <button
        type="button"
        class="btn-close"
        data-bs-dismiss="offcanvas"
        aria-label="Close"
      ></button>
    </div>
    <div class="offcanvas-body">
      <ObservationEdit {student} goal={selectedGoal} observation={null} />
    </div>
  {/if}
</div>

<style>
  .chart-container {
    padding-top: 5px;
    height: 40px;
    width: 40px;
  }

  .expanded-student-row {
    background-color: #f8f9fa;
  }

  .expand-student-button {
    padding: 2px 8px 2px 1px;
  }

  .expand-student-button:hover {
    background-color: #f8f9fa;
  }

  .caret-icon {
    display: inline-block;
    transition: transform 0.3s ease;
  }

  .rotated {
    transform: rotate(90deg);
  }

  .offcanvas-wide {
    width: 55vw !important;
  }
</style>
